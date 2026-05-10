"""Load tabular files (CSV, Excel) via pandas — Data Agent pipeline only (no RAG)."""

from pathlib import Path

import pandas as pd


STRUCTURED_EXTENSIONS = frozenset({".csv", ".xlsx", ".xls"})


def excel_engine(path_suffix: str) -> str | None:
    low = path_suffix.lower()
    if low.endswith(".xlsx"):
        return "openpyxl"
    if low.endswith(".xls"):
        return "xlrd"
    return None


def dataframe_key(filename: str, sheet: str | None = None) -> str:
    base = Path(filename).name
    if sheet:
        sheet_clean = "".join(c if c.isalnum() or c in "-._ " else "_" for c in sheet)
        return f"{base}::{sheet_clean.strip().replace(' ', '_')}"
    return base


def _unique_key(existing: dict, base: str) -> str:
    if base not in existing:
        return base
    i = 2
    while f"{base}__dup{i}" in existing:
        i += 1
    return f"{base}__dup{i}"


def load_csv_df(path: str) -> tuple[str, pd.DataFrame]:
    key = dataframe_key(Path(path).name)
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return key, pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode CSV {path}")


def load_structured_tables(paths: list[str]) -> dict[str, pd.DataFrame]:
    """Load all CSV/Excel paths into keyed DataFrames."""
    loaded: dict[str, pd.DataFrame] = {}

    for raw in paths:
        resolved = Path(raw).resolve()
        ext = resolved.suffix.lower()
        if ext not in STRUCTURED_EXTENSIONS:
            continue

        if ext == ".csv":
            key, df = load_csv_df(str(resolved))
            loaded[_unique_key(loaded, key)] = df
            continue

        engine = excel_engine(str(resolved))
        with pd.ExcelFile(str(resolved), engine=engine) as xl:
            basename = resolved.name
            for sheet_name in xl.sheet_names:
                df = pd.read_excel(xl, sheet_name=sheet_name)
                uniq = _unique_key(loaded, dataframe_key(basename, sheet_name))
                loaded[uniq] = df

    return loaded
