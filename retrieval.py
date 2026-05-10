def retrieve_docs(vectorstore, query):
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 5,
            "fetch_k": 15
        }
    )

    docs = retriever.invoke(query)

    return docs