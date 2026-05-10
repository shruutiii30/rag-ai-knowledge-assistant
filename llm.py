import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

MAX_CONTEXT_CHARS = 2500

_SYSTEM_PROMPT = """You are a document intelligence assistant.

Answer ONLY using the document excerpts supplied in the final user message (the "Context excerpts" section).

Use the preceding conversation turns to resolve pronouns and follow-ups (for example tie "its" / "they" / "that" back to entities already discussed).

IMPORTANT:
Mention page numbers in your answer wherever possible.

If partial information exists, summarize it.

Only say that you cannot find enough information / "I don't know" if nothing relevant appears in Context excerpts."""

def generate_answer(query, docs, conversation_history=None):
    conversation_history = conversation_history or []

    context_parts = []

    for doc in docs:
        page = doc.metadata.get("page", "Unknown")
        content = doc.page_content

        context_parts.append(
            f"[Page {page}]\n{content}"
        )

    context = "\n\n".join(context_parts)

    excerpt_block = f"""Use ONLY the following Context excerpts when answering.

Context excerpts:
{context[:MAX_CONTEXT_CHARS]}

Current question:
{query}

Answer concisely using the excerpts. Mention page numbers when citing."""

    messages = [{"role": "system", "content": _SYSTEM_PROMPT}]

    for turn in conversation_history:
        role = turn.get("role")
        content = (turn.get("content") or "").strip()
        if role not in ("user", "assistant") or not content:
            continue
        messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": excerpt_block})

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=messages,
        temperature=0
    )

    return response.choices[0].message.content