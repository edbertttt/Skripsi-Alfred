from __future__ import annotations

from datetime import date, datetime
from typing import Any

import numpy as np
import pandas as pd


def is_missing(value: Any) -> bool:
    return value is None or pd.isna(value)


def fmt_number(value: Any, digits: int = 4) -> str:
    if is_missing(value):
        return "N/A"
    return f"{float(value):,.{digits}f}"


def fmt_currency(value: Any, currency: str = "USD") -> str:
    if is_missing(value):
        return "N/A"
    return f"{currency} {float(value):,.2f}"


def fmt_percent(value: Any, digits: int = 2) -> str:
    if is_missing(value):
        return "N/A"
    numeric = float(value)
    return f"{numeric * 100:,.{digits}f}%"


def fmt_date(value: Any) -> str:
    if is_missing(value):
        return "N/A"
    if isinstance(value, str):
        parsed = pd.to_datetime(value, errors="coerce", utc=True)
        if not pd.isna(parsed):
            return parsed.strftime("%Y-%m-%d")
        return value
    if isinstance(value, pd.Timestamp):
        if value.tzinfo is not None:
            value = value.tz_convert("UTC")
        return value.strftime("%Y-%m-%d")
    if isinstance(value, (datetime, date)):
        return value.strftime("%Y-%m-%d")
    return str(value)


def pretty_label(name: str) -> str:
    label = str(name).replace("_", " ").strip()
    replacements = {
        "ms garch": "MS-GARCH",
        "sv": "SV",
        "var": "VaR",
        "cvar": "CVaR",
        "adf": "ADF",
        "kpss": "KPSS",
        "arch lm": "ARCH-LM",
        "ljung box": "Ljung-Box",
        "btc": "BTC",
        "usdt": "USDT",
        "pvalue": "p-value",
        "p value": "p-value",
        "q025": "2.5%",
        "q500": "50%",
        "q975": "97.5%",
    }
    lowered = label.lower()
    for old, new in replacements.items():
        lowered = lowered.replace(old, new)
    return lowered.title().replace("Ms-Garch", "MS-GARCH").replace("Cvar", "CVaR").replace("Var", "VaR")


def tidy_dataframe(df: pd.DataFrame, digits: int = 6) -> pd.DataFrame:
    if df.empty:
        return df

    display = df.copy()
    for column in display.columns:
        if pd.api.types.is_datetime64_any_dtype(display[column]):
            display[column] = display[column].dt.strftime("%Y-%m-%d")
        elif pd.api.types.is_numeric_dtype(display[column]):
            display[column] = display[column].replace([np.inf, -np.inf], np.nan).round(digits)

    display.columns = [pretty_label(column) for column in display.columns]
    return display


def format_pass_fail(value: Any) -> str:
    if is_missing(value):
        return "N/A"
    if isinstance(value, str):
        lowered = value.lower().strip()
        if lowered in {"true", "pass", "passed"}:
            return "Pass"
        if lowered in {"false", "fail", "failed"}:
            return "Fail"
    return "Pass" if bool(value) else "Fail"
