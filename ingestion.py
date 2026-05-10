from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader

# Unstructured ingestion only (structured files use pandas / Tabular Agent — see structured_ingestion.py)
UNSTRUCTURED_EXTENSIONS = frozenset({".pdf", ".txt", ".docx"})
STRUCTURED_EXTENSIONS_FOR_UPLOAD = frozenset({".csv", ".xlsx", ".xls"})
ALLOWED_EXTENSIONS = frozenset.union(UNSTRUCTURED_EXTENSIONS, STRUCTURED_EXTENSIONS_FOR_UPLOAD)


def is_allowed_extension(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def _load_txt(path: str) -> list[Document]:
    try:
        loader = TextLoader(path, encoding="utf-8", autodetect_encoding=True)
    except TypeError:
        loader = TextLoader(path, encoding="utf-8")

    docs = loader.load()
    basename = Path(path).name
    for d in docs:
        d.metadata.setdefault("source", basename)
        d.metadata.setdefault("page", None)
    return docs


def _load_docx(path: str) -> list[Document]:
    docs = Docx2txtLoader(path).load()
    basename = Path(path).name
    for d in docs:
        d.metadata.setdefault("source", basename)
        d.metadata.setdefault("page", None)
    return docs


def _load_pdf(path: str) -> list[Document]:
    return PyPDFLoader(path).load()


def load_document(path: str) -> list[Document]:
    ext = Path(path).suffix.lower()
    loaders = {
        ".pdf": _load_pdf,
        ".txt": _load_txt,
        ".docx": _load_docx,
    }

    loader = loaders.get(ext)
    if loader is None:
        raise ValueError(
            f"Unsupported unstructured type '{ext}' for LangChain ingestion. "
            f"Use: {sorted(UNSTRUCTURED_EXTENSIONS)}"
        )

    return loader(path)


def load_documents(file_paths):
    if not file_paths:
        return []

    documents = []
    for path in file_paths:
        resolved = Path(path)

        if not resolved.is_file():
            raise FileNotFoundError(path)

        if Path(resolved.name).suffix.lower() not in UNSTRUCTURED_EXTENSIONS:
            raise ValueError(
                f"{resolved.name}: not an unstructured document for RAG. "
                f"Expect: {sorted(UNSTRUCTURED_EXTENSIONS)}"
            )

        documents.extend(load_document(str(resolved.resolve())))

    return documents


def load_pdfs(file_paths):
    """Backward-compatible alias — loads unstructured documents for RAG."""
    return load_documents(file_paths)


def clean_text(documents):
    for doc in documents:
        doc.page_content = doc.page_content.replace("\n", " ")
    return documents
