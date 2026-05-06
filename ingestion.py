from langchain_community.document_loaders import PyPDFLoader

def load_pdfs(file_paths):
    documents = []

    for path in file_paths:
        loader = PyPDFLoader(path)   # open PDF
        docs = loader.load()         # read all pages

        documents.extend(docs)       # combine all pages

    return documents

def clean_text(documents):
    for doc in documents:
        doc.page_content = doc.page_content.replace("\n", " ")
    return documents