"""Data Agent: pandas execution guided by OpenRouter (no retrieval)."""

from __future__ import annotations

import logging
import re
from typing import Any

import numpy as np
import pandas as pd

from llm import client


log = logging.getLogger("tabular_agent")


_BAD_FRAG = (
    "import ",
    "eval(",
    "exec(",
    "open(",
    "compile(",
    "breakpoint(",
    "globals(",
    "locals(",
    "ctypes",
    "subprocess",
    "socket",
    "__import__",
)


_SYS_INSTRUCTION = (
    "Sandbox exposes pd numpy np dfs dict keyed by TABLE_KEY literals shown in CONTEXT."
    " Assign ANSWER as int float pandas Series or pandas DataFrame with at most forty rendered rows."
    " Disallow importing subprocess setattr getattr urllib disk network or builtins abuse beyond injected helpers."
    " Access dfs[exact repr TABLE_KEY from CONTEXT]. Respond with ONLY one fenced markdown python block."
    " The user prompt may combine prior analytical intent with new filters; "
    " map phrases like excluding/without/only/filter to pandas boolean masks "
    "(e.g. ~(col.str.upper().isin([...])) or .query), group by to .groupby, "
    " top/bottom N to nlargest/nsmallest or sort_values with head/tail."
    " Inspect COLUMNS_AS_LIST for order status/type columns matching cancelled/returned semantics."
)


_FILTER_TRIGGER = re.compile(
    r"(?ix)\b("
    r"excluding|exclude|without|omit|omitting|leave\s+out|"
    r"only|just|filter|where|having|except|unless|"
    r"(?:top|bottom|first|last)\s+\d+|"
    r"highest|lowest|largest|smallest|maximum|minimum|most|least|\bmax\b|\bmin\b|"
    r"group\s+by|breakdown\s+by|break\s+down\s+by|broken\s+down\s+by|"
    r"aggregate\s+by|split\s+by|each\b|"
    r"sort\s+by|order\s+by|rank(?:ed)?\s+by|"
    r"per\s+(?:region|department|city|country|month|year|week|category|segment|sku|vendor|seller|salesperson)"
    r")\b"
)


def _token_scan(blob: str) -> bool:
    lowered = blob.lower()
    return not any(fragment in lowered for fragment in _BAD_FRAG)


def _extract_block(text: str) -> str | None:
    marker = chr(96) * 3
    pattern = marker + r"(?:python)?\s*(.*?)\s*" + marker
    hit = re.search(pattern, text, flags=re.DOTALL | re.IGNORECASE)
    if hit is None:
        return None
    return hit.group(1).strip()


def _table_digest(frames: dict[str, pd.DataFrame], ceiling: int = 8400) -> str:
    pieces: list[str] = []
    spent = 0
    nl = chr(10)
    for label, frame in frames.items():
        chunk = nl.join(
            [
                "## TABLE",
                f"TABLE_KEY = {repr(label)}",
                f"ROWS = {len(frame)} COLS = {len(frame.columns)}",
                f"COLUMNS_AS_LIST = {list(frame.columns)}",
                "HEAD_PREVIEW",
                frame.head(12).to_string(),
                "DTYPES",
                frame.dtypes.astype(str).to_string(),
            ]
        )
        extra = ""
        try:
            numeric = frame.select_dtypes(include="number")
            if not numeric.empty:
                extra = nl + "NUMERIC_DESCRIBE" + nl + numeric.describe().to_string()
        except Exception:
            extra = ""
        slab = chunk + extra
        block = slab + nl * 2
        if spent + len(block) > ceiling:
            pieces.append(slab[: max(240, ceiling - spent)] + " [CLIP]")
            break
        pieces.append(slab)
        spent += len(block)
    return nl.join(pieces)


def _run_python(code: str, bundle: dict[str, pd.DataFrame]) -> tuple[Any | None, str | None]:
    env: dict[str, Any] = {
        "__builtins__": {},
        "len": len,
        "min": min,
        "max": max,
        "sum": sum,
        "sorted": sorted,
        "enumerate": enumerate,
        "zip": zip,
        "range": range,
        "round": round,
        "pow": pow,
        "abs": abs,
        "dict": dict,
        "list": list,
        "tuple": tuple,
        "set": set,
        "str": str,
        "float": float,
        "int": int,
        "bool": bool,
        "repr": repr,
        "isinstance": isinstance,
        "pd": pd,
        "np": np,
        "dfs": {k: v.copy() for k, v in bundle.items()},
        "ANSWER": None,
    }
    try:
        exec(compile(code, "<tabular_agent>", "exec"), env)
    except Exception as exc:
        return None, str(exc)
    return env.get("ANSWER"), None


def _present(value: Any) -> str:
    nl = chr(10)
    if isinstance(value, pd.DataFrame):
        clip = value.head(30)
        body = clip.to_string(index=True)
        if len(value.index) > 30:
            body = body + nl + "[more rows omitted]"
        return body
    if isinstance(value, pd.Series):
        clip = value.head(35)
        body = clip.to_string()
        if len(value.index) > 35:
            body = body + nl + "[more entries omitted]"
        return body
    return str(value)


def _sources(bundle: dict[str, pd.DataFrame]) -> list[dict]:
    rows: list[dict] = []
    for key, frame in bundle.items():
        preview = frame.head(3).to_string()
        rows.append(
            {
                "page": None,
                "content": f"Data Agent | {key} shape={frame.shape} preview={preview}",
            }
        )
    return rows


def _last_prior_user_turn(prior: list) -> tuple[str | None, bool]:
    """Latest prior user text, and whether the last stored turn is assistant (follow-up context)."""
    last_role = None
    for turn in reversed(prior):
        role = turn.get("role")
        if role in {"user", "assistant"}:
            last_role = role
            break
    last_user_content: str | None = None
    for turn in reversed(prior):
        if turn.get("role") == "user":
            text = (turn.get("content") or "").strip()
            last_user_content = text or None
            break
    return last_user_content, last_role == "assistant"


def _merge_prior_user_question(prev_user_q: str, follow_up: str) -> str:
    base = prev_user_q.strip().rstrip("?.! ").strip()
    frag = follow_up.strip()
    if frag and frag[0].isupper() and frag[0].isalpha():
        frag = frag[0].lower() + frag[1:]
    sep = "" if base.endswith((" ", "\n")) else " "
    return f"{base}{sep}{frag}".strip()


def _should_rewrite_tabular_followup(current: str, prior: list) -> bool:
    cur = (current or "").strip()
    if not cur:
        return False
    prev_user, after_assistant = _last_prior_user_turn(prior)
    if not prev_user or prev_user.strip() == cur:
        return False
    # Fragments typed after assistant context (canonical follow-ups)
    short_non_question = (
        len(cur) < 180
        and not re.search(r"[.?]\s*$", cur.strip())
        and not re.match(
            r"^(what|which|who|whose|when|why|how|show|list|calculate|compute|give|tell|find|count|sum|avg|plot)\b",
            cur,
            re.IGNORECASE,
        )
    )
    if _FILTER_TRIGGER.search(cur):
        return True
    if after_assistant and short_non_question:
        return True
    return False


def rewrite_tabular_query_for_memory(prompt: str, prior: list | None) -> tuple[str, str]:
    """Return (effective_prompt, original_prompt). effective_prompt merges last user Q + follow-up when needed."""
    original = (prompt or "").strip()
    prior_list = prior or []
    if not original or not _should_rewrite_tabular_followup(original, prior_list):
        return original, original
    prev_user, _after_asst = _last_prior_user_turn(prior_list)
    if not prev_user:
        return original, original
    merged = _merge_prior_user_question(prev_user, original)
    return merged if merged != original else original, original


def answer_tabular_query(
    prompt: str,
    bundle: dict[str, pd.DataFrame],
    history: list | None = None,
) -> tuple[str, list[dict]]:
    prior = history or []
    effective_prompt, original_prompt = rewrite_tabular_query_for_memory(prompt, prior)
    log.info(
        "Data Agent mode: intent before pandas sandbox (after conversational rewrite) | intent=%r | raw_turn=%r | merged_with_prior=%s",
        effective_prompt,
        original_prompt,
        effective_prompt != original_prompt,
    )

    digest = _table_digest(bundle)
    nl = chr(10)
    chat = [{"role": "system", "content": _SYS_INSTRUCTION + nl + digest}]
    for turn in prior:
        role = turn.get("role")
        text = (turn.get("content") or "").strip()
        if role not in {"user", "assistant"} or not text:
            continue
        chat.append({"role": role, "content": text})
    chat.append({"role": "user", "content": effective_prompt})

    thread: list[dict] = []
    last_err = ""
    for _ in range(3):
        reply = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=chat + thread,
            temperature=0,
            max_tokens=1100,
        )
        raw = reply.choices[0].message.content or ""
        block = _extract_block(raw)
        if not block:
            last_err = "missing_python_fence"
            thread.extend(
                [
                    {"role": "assistant", "content": raw},
                    {
                        "role": "user",
                        "content": "You must output exactly one fenced markdown python block.",
                    },
                ]
            )
            continue
        if not _token_scan(block):
            last_err = "forbidden_substring"
            thread.extend(
                [
                    {"role": "assistant", "content": raw},
                    {
                        "role": "user",
                        "content": "Remove forbidden calls like import eval exec open.",
                    },
                ]
            )
            continue
        value, glitch = _run_python(block, bundle)
        if glitch:
            last_err = glitch
            thread.extend(
                [
                    {"role": "assistant", "content": raw},
                    {"role": "user", "content": f"Runtime error: {glitch}"},
                ]
            )
            continue
        if value is None:
            last_err = "answer_was_none"
            thread.extend(
                [
                    {"role": "assistant", "content": raw},
                    {
                        "role": "user",
                        "content": (
                            "ANSWER resolved to None. Build a dataframe filter for exclude/only phrases "
                            "from the rewritten question (e.g. status column), aggregate, and set ANSWER to "
                            "a numeric or table result."
                        ),
                    },
                ]
            )
            continue
        body = _present(value)
        if len(body) > 9000:
            body = body[:8900] + nl + "[tail clipped]"
        return body, _sources(bundle)

    msg = "Tabular agent failed. Last detail: " + (last_err or "unknown")
    return msg, _sources(bundle)
