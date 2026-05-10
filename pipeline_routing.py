"""Route each /ask request to the right backend.

Unstructured files (PDF, TXT, DOCX) are indexed for RAG; structured files
(CSV, XLSX, XLS) are loaded into pandas for the Data Agent only.

- Only RAG loaded → RAG mode.
- Only tabular loaded → Data Agent mode.
- Both loaded → keyword hints, then OpenRouter JSON classification if ambiguous.
"""

from __future__ import annotations

import json
import re

from llm import client


_DATA_HINT = re.compile(
    r"\b("
    r"sum|sums|total|totals|aggregate|aggregates|average|avg|mean|median|"
    r"minimum|maximum|min|max|count|corr|growth|pct|percentage|histogram|skew|"
    r"distinct|spreadsheet|dataframe|profit|revenue|sales|quantity|sku|"
    r"region|product|pivot|group\s+by|rank|ranking|compare|comparison|"
    r"highest|lowest|largest|smallest|greatest|least"
    r")\b|"
    r"\b(top|bottom|first|last)\s+\d+",
    re.IGNORECASE,
)

_DOC_HINT = re.compile(
    r"\b("
    r"summary|summarize|clause|explain|according|introduction|chapter|"
    r"cite|citation|referenced|quoted|verbatim|paragraph|section|"
    r"page|pages|document|policy|contract|agreement|what\s+does\s+the\s+text"
    r")\b",
    re.IGNORECASE,
)


def route_ask_pipeline(query: str, has_rag: bool, has_tabular: bool) -> str:
    if has_rag and not has_tabular:
        return "rag"
    if has_tabular and not has_rag:
        return "data"
    if not has_rag and not has_tabular:
        return "none"

    q = query.strip()
    dq = _DATA_HINT.search(q)
    aq = _DOC_HINT.search(q)
    if dq and not aq:
        return "data"
    if aq and not dq:
        return "rag"
    return _dispatch_dual_with_llm(q)


def _dispatch_dual_with_llm(question: str) -> str:
    msgs = [
        {
            "role": "system",
            "content": (
                "Classify routing for a hybrid assistant serving both document snippets (PDF/Word/Text) "
                "and quantitative spreadsheet tables loaded in pandas.\n"
                'Reply with JSON only: {\"pipeline\":\"rag\"} for narrative/policy/document lookups, '
                'or {\"pipeline\":\"data\"} for computations, aggregates, comparisons, pivots over tables.'
            ),
        },
        {"role": "user", "content": question},
    ]
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=msgs,
        temperature=0,
        max_tokens=32,
        response_format={"type": "json_object"},
    )
    raw = (response.choices[0].message.content or "{}").strip()
    try:
        payload = json.loads(raw)
        mode = payload.get("pipeline") or ""
    except json.JSONDecodeError:
        mode = ""

    normalized = (mode or "").lower().strip()
    return "rag" if normalized.startswith("rag") else "data"
