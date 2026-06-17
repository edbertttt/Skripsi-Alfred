from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
import streamlit as st


BINANCE_API_BASES = (
    "https://api.binance.com",
    "https://api1.binance.com",
    "https://api2.binance.com",
    "https://data-api.binance.vision",
)
SYMBOL = "BTCUSDT"
REQUEST_TIMEOUT = 4

TIMEFRAME_CONFIG = {
    "1D": {"interval": "1h", "limit": 24},
    "7D": {"interval": "4h", "limit": 42},
    "30D": {"interval": "1d", "limit": 30},
    "90D": {"interval": "1d", "limit": 90},
    "1Y": {"interval": "1d", "limit": 365},
}


@st.cache_data(ttl=10, show_spinner=False)
def fetch_realtime_ticker() -> tuple[dict, str | None]:
    try:
        payload = _get_json("/api/v3/ticker/24hr", {"symbol": SYMBOL})
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {}, _friendly_error("latest ticker", exc)
    return payload, None


@st.cache_data(ttl=180, show_spinner=False)
def fetch_price_klines(timeframe: str) -> tuple[pd.DataFrame, str | None]:
    config = TIMEFRAME_CONFIG.get(timeframe, TIMEFRAME_CONFIG["30D"])
    try:
        payload = _get_json(
            "/api/v3/klines",
            {
                "symbol": SYMBOL,
                "interval": config["interval"],
                "limit": config["limit"],
            },
        )
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return pd.DataFrame(), _friendly_error("price candles", exc)

    return _klines_to_dataframe(payload), None


def merge_daily_realtime(base_df: pd.DataFrame, daily_df: pd.DataFrame) -> pd.DataFrame:
    if base_df.empty:
        return daily_df
    if daily_df.empty:
        return base_df

    merged = pd.concat([base_df, daily_df], ignore_index=True, sort=False)
    if "open_time" not in merged.columns:
        return merged
    merged = merged.sort_values("open_time")
    merged = merged.drop_duplicates(subset=["open_time"], keep="last")
    merged["ret_log"] = _fill_log_return(merged)
    merged["loss"] = -merged["ret_log"]
    if "rolling_vol_30d" in merged.columns:
        existing_vol = pd.to_numeric(merged["rolling_vol_30d"], errors="coerce")
        computed_vol = pd.to_numeric(merged["ret_log"], errors="coerce").rolling(30).std()
        merged["rolling_vol_30d"] = existing_vol.fillna(computed_vol)
    return merged.reset_index(drop=True)


def ticker_last_price(ticker: dict) -> float | None:
    value = ticker.get("lastPrice")
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def ticker_change_percent(ticker: dict) -> float | None:
    value = ticker.get("priceChangePercent")
    if value is None:
        return None
    try:
        return float(value) / 100
    except (TypeError, ValueError):
        return None


def _get_json(endpoint: str, params: dict[str, str | int]) -> dict | list:
    errors: list[str] = []
    for base_url in BINANCE_API_BASES:
        url = f"{base_url}{endpoint}?{urlencode(params)}"
        request = Request(url, headers={"User-Agent": "BTC-Risk-Dashboard/1.0"})
        try:
            with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            errors.append(f"{base_url}: {exc}")

    raise URLError("; ".join(errors))


def _klines_to_dataframe(payload: list) -> pd.DataFrame:
    if not payload:
        return pd.DataFrame()

    columns = [
        "open_time_ms",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time_ms",
        "quote_asset_volume",
        "number_of_trades",
        "taker_buy_base_volume",
        "taker_buy_quote_volume",
        "ignore",
    ]
    df = pd.DataFrame(payload, columns=columns)
    numeric_columns = ["open", "high", "low", "close", "volume"]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["open_time"] = pd.to_datetime(df["open_time_ms"], unit="ms", utc=True)
    df["close_time"] = pd.to_datetime(df["close_time_ms"], unit="ms", utc=True)
    df = df[["open_time", "open", "high", "low", "close", "volume", "close_time"]]
    df["ret_log"] = _fill_log_return(df)
    df["loss"] = -df["ret_log"]
    df["rolling_vol_30d"] = df["ret_log"].rolling(30).std()
    return df.dropna(subset=["open_time", "close"])


def _fill_log_return(df: pd.DataFrame) -> pd.Series:
    close = pd.to_numeric(df["close"], errors="coerce")
    computed = pd.Series(pd.NA, index=df.index, dtype="Float64")
    valid = close.gt(0) & close.shift(1).gt(0)
    computed.loc[valid] = np.log(close.loc[valid] / close.shift(1).loc[valid])
    if "ret_log" in df.columns:
        original = pd.to_numeric(df["ret_log"], errors="coerce").astype("Float64")
        return original.fillna(computed)
    return computed


def _friendly_error(resource: str, exc: Exception) -> str:
    message = str(exc)
    if "Connection refused" in message or "Errno 61" in message:
        reason = "connection refused by the local network, firewall, ISP, or Binance endpoint"
    elif "timed out" in message.lower():
        reason = "request timed out"
    else:
        reason = "request failed"
    return f"Live Binance {resource} could not be retrieved ({reason})."
