from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,      # max characters per chunk
        chunk_overlap=50    # overlap for context continuity
    )

    chunks = splitter.split_documents(documents)
    return chunks