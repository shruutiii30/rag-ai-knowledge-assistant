import logging
import os
import shutil
from pathlib import Path

import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from chunking import chunk_documents
from embeddings import create_vector_store, load_vector_store
from ingestion import (
    ALLOWED_EXTENSIONS,
    UNSTRUCTURED_EXTENSIONS,
    clean_text,
    is_allowed_extension,
    load_documents,
)
from llm import generate_answer
from pipeline_routing import route_ask_pipeline
from retrieval import retrieve_docs
from structured_ingestion import STRUCTURED_EXTENSIONS, load_structured_tables
from tabular_agent import answer_tabular_query
from tabular_store import TabularStore


logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
log = logging.getLogger("hybrid_rag")

try:
    vectorstore = load_vector_store()
    log.info("Vector store loaded from disk (RAG mode ready if used).")
except Exception:
    vectorstore = None


tabular_store = TabularStore()

# Completed turns only: {"role": "user"|"assistant", "content": str}; trimmed to MAX_STORED_MESSAGES
chat_history = []

MAX_CONVERSATION_EXCHANGES = 3
MAX_STORED_MESSAGES = MAX_CONVERSATION_EXCHANGES * 2

def _prior_turns_for_prompt():
    return chat_history[-MAX_STORED_MESSAGES:]

def _truncate_for_embedding(text: str, max_len: int = 700):
    text = (text or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"

def build_retrieval_query(current_query: str, prior_turns: list):
    """Combine recent dialogue with the latest question so MMR retrieves relevant passages for follow-ups."""
    parts = []

    lines = []
    for turn in prior_turns:
        role = turn.get("role")
        content = (turn.get("content") or "").strip()
        if not content or role not in ("user", "assistant"):
            continue
        label = "User" if role == "user" else "Assistant"
        if role == "assistant":
            content = _truncate_for_embedding(content)
        lines.append(f"{label}: {content}")

    if lines:
        parts.append("Recent conversation:")
        parts.extend(lines)
        parts.append("")

    parts.append(f"Retrieve passages that answer this question (resolve pronouns using the dialogue above).\nQuestion: {_truncate_for_embedding(current_query, max_len=2000)}")
    return "\n".join(parts)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "data"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store uploaded file paths temporarily
uploaded_files_list = []


def _canonical_upload_path(client_sent_path: str) -> str | None:
    """Resolve client-reported paths to files under UPLOAD_FOLDER (basename only)."""
    basename = os.path.basename(client_sent_path or "")
    if not basename:
        return None
    root = os.path.abspath(UPLOAD_FOLDER)
    full = os.path.abspath(os.path.join(root, basename))
    try:
        if os.path.commonpath([root, full]) != root:
            return None
    except ValueError:
        return None
    return full

@app.route("/")
def home():
    return "RAG API is running"


# ✅ UPLOAD API
@app.route("/upload", methods=["POST"])
def upload_files():
    global uploaded_files_list

    files = request.files.getlist("files")

    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    file_paths = []

    for file in files:
        if not file.filename:
            return jsonify({"error": "One or more uploads have no filename"}), 400
        if not is_allowed_extension(file.filename):
            return (
                jsonify(
                    {
                        "error": f"Unsupported file type for {file.filename!r}. "
                        "Allowed extensions: "
                        + ", ".join(sorted(ALLOWED_EXTENSIONS)),
                        "allowed_extensions": sorted(ALLOWED_EXTENSIONS),
                    }
                ),
                400,
            )
        safe_name = secure_filename(file.filename)
        if not safe_name:
            return jsonify({"error": "Invalid filename after sanitization"}), 400
        path = os.path.join(UPLOAD_FOLDER, safe_name)
        file.save(path)
        file_paths.append(path)

    uploaded_files_list = file_paths

    return jsonify({"message": "Files uploaded successfully", "paths": file_paths})


# ✅ PROCESS API
@app.route("/process", methods=["POST"])
def process_files():
    global vectorstore

    data = request.json or {}
    file_paths = data.get("file_paths")

    if not file_paths:
        return jsonify({"error": "file_paths required"}), 400

    canonical_paths = []
    for fp in file_paths:
        full = _canonical_upload_path(fp if isinstance(fp, str) else "")
        if full is None or not os.path.isfile(full):
            return jsonify({"error": f"File not found or invalid path: {fp!r}"}), 400
        if not is_allowed_extension(full):
            return jsonify({"error": f"Unsupported type: {full}"}), 400
        canonical_paths.append(full)

    unstructured_paths = [
        p
        for p in canonical_paths
        if Path(p).suffix.lower() in UNSTRUCTURED_EXTENSIONS
    ]
    structured_paths = [
        p for p in canonical_paths if Path(p).suffix.lower() in STRUCTURED_EXTENSIONS
    ]

    if structured_paths:
        try:
            frames = load_structured_tables(structured_paths)
        except (OSError, ValueError) as exc:
            return jsonify({"error": f"Structured ingest failed: {exc}"}), 400
        tabular_store.replace_all(frames)
        log.info(
            "Process: Data Agent — loaded %s table(s) from CSV/Excel (pandas cache, no RAG).",
            len(frames),
        )
    else:
        tabular_store.clear()
        log.info("Process: cleared tabular cache (no structured files in batch).")

    chunk_total = 0
    if unstructured_paths:
        try:
            docs = load_documents(unstructured_paths)
        except (FileNotFoundError, ValueError) as exc:
            return jsonify({"error": str(exc)}), 400

        docs = clean_text(docs)
        chunks = chunk_documents(docs)
        chunk_total = len(chunks)
        vectorstore = create_vector_store(chunks)
        log.info(
            "Process: RAG mode — FAISS index rebuilt (%s chunks from PDF/TXT/DOCX).",
            chunk_total,
        )
    else:
        vectorstore = None
        shutil.rmtree("faiss_index", ignore_errors=True)
        log.info("Process: no unstructured files; vector store cleared (structured-only batch).")

    log.info(
        "Ingestion split: RAG-eligible file(s)=%s, structured file(s)=%s",
        len(unstructured_paths),
        len(structured_paths),
    )

    if vectorstore is None and not tabular_store.nonempty():
        return jsonify({"error": "Nothing was ingested."}), 400

    return jsonify(
        {
            "message": "Ingestion complete",
            "total_chunks": chunk_total,
            "tabular_tables": len(tabular_store.frames),
        }
    )

#-----ASK ENDPOINT-----#
@app.route("/ask", methods=["POST"])
def ask_question():
    global vectorstore, chat_history

    data = request.json or {}
    query = data.get("query")
    if not query or not str(query).strip():
        return jsonify({"error": "Missing or empty query"}), 400
    query = str(query).strip()

    prior_turns = _prior_turns_for_prompt()
    has_rag = vectorstore is not None
    has_tabular = tabular_store.nonempty()
    if not has_rag and not has_tabular:
        return jsonify({"error": "No knowledge loaded. Process files first."}), 503

    mode = route_ask_pipeline(query, has_rag, has_tabular)
    if mode == "none":
        return jsonify({"error": "No knowledge loaded. Process files first."}), 503

    if mode == "data":
        log.info("Pipeline: Data Agent mode")
        bundle_raw = tabular_store.as_dict()
        bundle = {k: v for k, v in bundle_raw.items() if isinstance(v, pd.DataFrame)}
        if not bundle:
            return jsonify({"error": "Structured tables are unavailable."}), 503
        answer, sources = answer_tabular_query(query, bundle, prior_turns)
    else:
        log.info("Pipeline: RAG mode")
        if vectorstore is None:
            return jsonify({"error": "Vector store unavailable for RAG routing."}), 503
        retrieval_query = build_retrieval_query(query, prior_turns)
        docs = retrieve_docs(vectorstore, retrieval_query)
        for idx, doc in enumerate(docs):
            log.debug(
                "RAG retrieved chunk %s source=%s page=%s preview=%s",
                idx + 1,
                doc.metadata.get("source"),
                doc.metadata.get("page"),
                doc.page_content[:160],
            )
        answer = generate_answer(query, docs, conversation_history=prior_turns)
        sources = []
        for doc in docs:
            src = {
                "page": doc.metadata.get("page"),
                "content": doc.page_content[:200],
            }
            if doc.metadata.get("source") is not None:
                src["source"] = doc.metadata.get("source")
            sources.append(src)

    chat_history.append({"role": "user", "content": query})
    chat_history.append({"role": "assistant", "content": answer})
    if len(chat_history) > MAX_STORED_MESSAGES:
        chat_history[:] = chat_history[-MAX_STORED_MESSAGES:]

    return jsonify({"question": query, "answer": answer, "sources": sources})


if __name__ == "__main__":
    app.run(
    debug=True,
    use_reloader=False
)