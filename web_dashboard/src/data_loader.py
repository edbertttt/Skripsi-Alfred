from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from src.constants import (
    APP_DIR,
    CSV_FILES,
    DATE_COLUMN_BY_KEY,
    DATE_COLUMNS,
    FALLBACK_OUTPUT_DIR_NAMES,
    JSON_FILES,
    OUTPUT_DIR_NAMES,
    PROJECT_ROOT,
)


def resolve_output_dir() -> tuple[Path, list[str]]:
    for output_dir in _candidate_output_dirs(OUTPUT_DIR_NAMES):
        if output_dir.exists():
            return output_dir, []

    for fallback_dir in _candidate_output_dirs(FALLBACK_OUTPUT_DIR_NAMES):
        if fallback_dir.exists():
            return fallback_dir, [
                "`outputs/` folder was not found. Using the available exported outputs "
                f"from `{_display_path(fallback_dir)}`."
            ]

    return PROJECT_ROOT / "outputs", [
        "`outputs/` folder was not found. Add the required exported output files before opening the dashboard."
    ]


def file_exists(output_dir: str | Path, filename: str) -> bool:
    return (Path(output_dir) / filename).exists()


@st.cache_data(ttl=30, show_spinner=False)
def load_csv(output_dir: str, filename: str) -> pd.DataFrame:
    path = Path(output_dir) / filename
    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)
    df = _clean_index_columns(df, filename)
    df = _parse_date_columns(df)
    return df


@st.cache_data(ttl=30, show_spinner=False)
def load_json(output_dir: str, filename: str) -> dict[str, Any]:
    path = Path(output_dir) / filename
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_outputs(output_dir: Path) -> dict[str, Any]:
    output_dir_str = str(output_dir)
    data: dict[str, Any] = {
        key: load_csv(output_dir_str, filename) for key, filename in CSV_FILES.items()
    }
    data.update({key: load_json(output_dir_str, filename) for key, filename in JSON_FILES.items()})
    return data


def filter_outputs_by_date(
    data: dict[str, Any],
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> dict[str, Any]:
    filtered: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, pd.DataFrame):
            date_column = DATE_COLUMN_BY_KEY.get(key)
            filtered[key] = filter_by_date(value, start_date, end_date, date_column)
        else:
            filtered[key] = value
    return filtered


def filter_by_date(
    df: pd.DataFrame,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    date_column: str | None = None,
) -> pd.DataFrame:
    if df.empty:
        return df

    column = date_column or _detect_date_column(df)
    if column is None or column not in df.columns:
        return df

    start = pd.Timestamp(start_date).tz_localize("UTC") if pd.Timestamp(start_date).tzinfo is None else pd.Timestamp(start_date).tz_convert("UTC")
    end = pd.Timestamp(end_date).tz_localize("UTC") if pd.Timestamp(end_date).tzinfo is None else pd.Timestamp(end_date).tz_convert("UTC")
    end = end + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)

    mask = (df[column] >= start) & (df[column] <= end)
    return df.loc[mask].copy()


def available_date_bounds(data: dict[str, Any]) -> tuple[pd.Timestamp | None, pd.Timestamp | None]:
    date_ranges: list[tuple[pd.Timestamp, pd.Timestamp]] = []
    for key in ("btc", "risk", "price_demo", "ms_filtered_prob", "sv_latent"):
        df = data.get(key)
        if not isinstance(df, pd.DataFrame) or df.empty:
            continue
        column = DATE_COLUMN_BY_KEY.get(key) or _detect_date_column(df)
        if column is None or column not in df.columns:
            continue
        series = df[column].dropna()
        if not series.empty:
            date_ranges.append((series.min(), series.max()))

    if not date_ranges:
        return None, None
    return min(start for start, _ in date_ranges), max(end for _, end in date_ranges)


def missing_files(output_dir: Path, keys: list[str]) -> list[str]:
    missing: list[str] = []
    for key in keys:
        filename = CSV_FILES.get(key) or JSON_FILES.get(key)
        if filename and not file_exists(output_dir, filename):
            missing.append(filename)
    return missing


def _clean_index_columns(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    unnamed_columns = [column for column in df.columns if str(column).startswith("Unnamed:")]
    if not unnamed_columns:
        return df

    df = df.copy()
    for column in unnamed_columns:
        if filename.startswith("ljung_box"):
            df = df.rename(columns={column: "lag"})
        elif filename == "ms_garch_transition_matrix.csv":
            df = df.rename(columns={column: "from_state"})
        else:
            df = df.rename(columns={column: "index"})
    return df


def _parse_date_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for column in DATE_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce", utc=True)
    return df


def _detect_date_column(df: pd.DataFrame) -> str | None:
    for column in DATE_COLUMNS:
        if column in df.columns:
            return column
    return None


def _candidate_output_dirs(names: tuple[str, ...]) -> list[Path]:
    roots = [Path.cwd(), APP_DIR, PROJECT_ROOT]
    candidates: list[Path] = []
    seen: set[Path] = set()

    for root in roots:
        for name in names:
            candidate = (root / name).resolve()
            if candidate not in seen:
                candidates.append(candidate)
                seen.add(candidate)

    return candidates


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)
