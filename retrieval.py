def retrieve_docs(vectorstore, query):
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 4,          # final docs returned
            "fetch_k": 10    # candidates before filtering
        }
    )

    docs = retriever.invoke(query)
    return docs