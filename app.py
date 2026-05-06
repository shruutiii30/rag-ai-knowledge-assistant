from flask import Flask, request, jsonify
from flask_cors import CORS
from ingestion import load_pdfs, clean_text
from chunking import chunk_documents
from embeddings import create_vector_store
import os
from retrieval import retrieve_docs
from llm import generate_answer
from embeddings import load_vector_store

try:
    vectorstore = load_vector_store()
    print("✅ Vector store loaded")
except:
    vectorstore = None
    
vectorstore = None

chat_history = []

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "data"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store uploaded file paths temporarily
uploaded_files_list = []

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
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)
        file_paths.append(path)

    uploaded_files_list = file_paths  # store for later use

    return jsonify({
        "message": "Files uploaded successfully",
        "paths": file_paths
    })


# ✅ PROCESS API
@app.route("/process", methods=["POST"])
def process_files():
    global vectorstore

    data = request.json
    file_paths = data.get("file_paths")

    # Step 1: Load
    docs = load_pdfs(file_paths)

    # Step 2: Clean
    docs = clean_text(docs)

    # Step 3: Chunk
    chunks = chunk_documents(docs)

    # Step 4: Embedding + Store
    vectorstore = create_vector_store(chunks)

    return jsonify({
        "message": "Vector store created",
        "total_chunks": len(chunks)
    })

#-----ASK ENDPOINT-----#
@app.route("/ask", methods=["POST"])
def ask_question():
    global vectorstore, chat_history

    if vectorstore is None:
        return jsonify({"error": "No documents processed yet"})

    data = request.json
    query = data.get("query")

    # Add previous context
    history_text = "\n".join(chat_history[-3:])  # last 3 messages

    enhanced_query = f"""
    Previous conversation:
    {history_text}

    Current question:
    {query}
    """

    docs = retrieve_docs(vectorstore, enhanced_query)

    answer = generate_answer(query, docs)

    # Save conversation
    chat_history.append(f"Q: {query}")
    chat_history.append(f"A: {answer}")

    return jsonify({
        "question": query,
        "answer": answer,
        "sources": [
            {
                "page": doc.metadata.get("page"),
                "content": doc.page_content[:200]
            }
            for doc in docs
        ]
    })


if __name__ == "__main__":
    app.run(debug=True)