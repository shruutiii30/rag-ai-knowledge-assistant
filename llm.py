from transformers import pipeline

generator = pipeline(
    "text-generation",
    model="distilgpt2"
)

def generate_answer(query, docs):
    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
    Based on the context below, answer the question briefly.
    If the answer is not present, say "I don't know."

    Context:
    {context[:800]}

    Question:
    {query}

    Answer:
    """

    response = generator(
        prompt,
        max_new_tokens=80,
        do_sample=False
    )

    generated_text = response[0]["generated_text"]

    # Return only answer part
    if "Answer:" in generated_text:
        return generated_text.split("Answer:")[-1].strip()

    return generated_text