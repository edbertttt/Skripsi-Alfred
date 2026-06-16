from __future__ import annotations

import sys
import math
from html import escape
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from src import charts
from src.components import (
    info_card,
    live_price_card,
    metric_grid,
    note,
    page_header,
    realtime_backtesting_panel,
    realtime_forecast_panel,
    realtime_risk_charts,
    render_plotly,
    render_table,
    set_global_styles,
    sidebar_title,
    status_message,
    warn_missing_many,
)
from src.constants import (
    APP_TITLE,
    AUTHOR,
    CONFIDENCE_OPTIONS,
    MODEL_KEYS,
    MODEL_LABELS,
    MODEL_OPTIONS,
    PAGES,
    THESIS_TITLE,
)
from src.data_loader import (
    available_date_bounds,
    load_outputs,
    missing_files,
    resolve_output_dir,
)
from src.formatting import (
    fmt_currency,
    fmt_date,
    fmt_number,
    fmt_percent,
    format_pass_fail,
    is_missing,
)
from src.realtime import (
    fetch_price_klines,
    merge_daily_realtime,
)


OUTPUT_DIR: Path | None = None
RAW_DATA: dict[str, Any] = {}
DATA: dict[str, Any] = {}


def render_dashboard(filters: dict[str, Any]) -> None:
    page_header(
        "Dashboard",
        "Bitcoin Volatility and Risk Analytics",
    )
    filters = _page_filter_controls("dashboard", filters)

    btc_df = DATA["btc"]
    risk_df = DATA["risk"]
    warn_missing_many(missing_files(OUTPUT_DIR, ["btc", "risk"]))

    price_timeframe = st.session_state.get("dashboard_price_timeframe", "30D")
    realtime_klines, _kline_warning = fetch_price_klines("30D" if price_timeframe == "All" else price_timeframe)

    price_chart_df = _price_chart_data(btc_df, realtime_klines, price_timeframe)
    btc_metric_df = merge_daily_realtime(btc_df, realtime_klines) if not realtime_klines.empty else btc_df

    latest_btc = _latest_row(btc_metric_df)
    latest_risk = _latest_row(risk_df)
    selected_models = _selected_models(filters["model"])
    confidence = filters["confidence"]

    live_price_card(
        price=_value(latest_btc, "close"),
        change_percent=_value(latest_btc, "ret_log"),
        updated_at=_format_live_timestamp(
            _first_available(_value(latest_btc, "close_time"), _value(latest_btc, "open_time"))
        ),
    )

    metric_grid(
        [
            {"label": "Latest Log Return", "value": fmt_percent(_value(latest_btc, "ret_log"))},
            {
                "label": "Latest Volatility",
                "value": _latest_model_values(latest_risk, selected_models, "{model}_sigma", percent=True),
            },
            {
                "label": f"Latest VaR {filters['confidence_label']}",
                "value": _latest_model_values(latest_risk, selected_models, f"{{model}}_VaR_{confidence}", percent=True),
            },
            {
                "label": f"Latest CVaR {filters['confidence_label']}",
                "value": _latest_model_values(latest_risk, selected_models, f"{{model}}_CVaR_{confidence}", percent=True),
            },
            {
                "label": "High Volatility State Probability",
                "value": fmt_percent(_value(latest_risk, "MS_GARCH_p_high")),
            },
            {
                "label": "VaR Breach Status",
                "value": _latest_breach_status(latest_risk, selected_models, confidence),
            },
        ]
    )

    price_timeframe = _render_price_chart_section(price_chart_df, price_timeframe)
    if price_timeframe == "All":
        note(
            "All-time BTC price is shown on a log scale so early-period and recent-period movements remain readable. "
            "Use the bottom range slider to zoom and scroll."
        )
    else:
        note("Use the bottom range slider to zoom and scroll through BTCUSDT close prices.")

    realtime_risk_charts(btc_df, risk_df, filters["model"], confidence)


def render_models_diagnostics(filters: dict[str, Any]) -> None:
    page_header(
        "Models & Diagnostics",
        "Model outputs, volatility paths, and statistical diagnostics from the final notebook pipeline.",
    )
    filters = _page_filter_controls("models", filters)

    warn_missing_many(
        missing_files(
            OUTPUT_DIR,
            [
                "model_rank",
                "best_model",
                "ms_params",
                "ms_transition",
                "ms_filtered_prob",
                "ms_state_vol",
                "sv_params",
                "sv_latent",
                "stationarity",
                "ljung_return",
                "ljung_squared",
                "arch_lm",
                "distribution",
            ],
        )
    )

    overview_tab, ms_tab, sv_tab, diagnostics_tab = st.tabs(
        ["Overview", "MS-GARCH", "Stochastic Volatility", "Diagnostics Notes"]
    )

    with overview_tab:
        st.markdown(
            """
            BTCUSDT OHLCV -> preprocessing -> log return -> ARMA mean filtering ->
            MS-GARCH and Stochastic Volatility -> VaR/CVaR -> out-of-sample backtesting.
            """
        )
        st.caption(
            "Model estimation, risk forecasting, and evaluation outputs are prepared from the statistical workflow "
            "and summarized here for thesis review."
        )
        col1, col2 = st.columns(2)
        with col1:
            render_table(
                _overview_model_table(DATA["model_rank"], filters["model"], filters["confidence"]),
                f"Model Comparison Summary ({filters['confidence_label']})",
                "Model comparison summary is not available.",
            )
        with col2:
            render_table(
                _overview_model_table(DATA["best_model"], "COMPARE", filters["confidence"]),
                f"Best Model by Confidence Level ({filters['confidence_label']})",
                "Best model summary is not available.",
            )

    with ms_tab:
        st.markdown(
            "MS-GARCH captures two volatility regimes: a low volatility state and a high volatility state."
        )
        col1, col2 = st.columns(2)
        with col1:
            render_table(DATA["ms_params"], "MS-GARCH Parameter Table", "MS-GARCH parameters are not available.")
        with col2:
            render_table(
                DATA["ms_transition"],
                "MS-GARCH Transition Matrix",
                "MS-GARCH transition matrix is not available.",
            )
        render_plotly(charts.high_vol_probability_chart(_preferred_ms_probability(), DATA["risk"]))
        note("Higher probability indicates stronger evidence that Bitcoin returns are in the high volatility regime.")
        render_plotly(charts.ms_state_volatility_chart(DATA["ms_state_vol"]))
        note("The state volatility paths describe the conditional risk level implied by each MS-GARCH regime.")

    with sv_tab:
        st.markdown("Stochastic Volatility treats volatility as a latent stochastic process.")
        render_table(
            DATA["sv_params"],
            "SV Posterior Parameter Summary",
            "SV posterior parameters are not available.",
        )
        render_plotly(charts.sv_latent_volatility_chart(DATA["sv_latent"]))
        note(
            "The latent volatility path summarizes posterior volatility estimates. If available, the band shows "
            "the 95% credible interval."
        )

    with diagnostics_tab:
        st.markdown(
            """
            ADF and KPSS evaluate stationarity. Ljung-Box checks autocorrelation.
            ARCH-LM and squared-return diagnostics indicate volatility clustering.
            Jarque-Bera, skewness, and kurtosis summarize non-normality and heavy tails.
            """
        )
        diag_tabs = st.tabs(["ADF / KPSS", "Ljung-Box", "ARCH-LM", "Distribution / Tail"])
        with diag_tabs[0]:
            render_table(DATA["stationarity"], missing_label="Stationarity diagnostics are not available.")
        with diag_tabs[1]:
            col1, col2 = st.columns(2)
            with col1:
                render_table(DATA["ljung_return"], "Return", "Ljung-Box return diagnostics are not available.")
            with col2:
                render_table(
                    DATA["ljung_squared"],
                    "Squared Return",
                    "Ljung-Box squared return diagnostics are not available.",
                )
        with diag_tabs[2]:
            render_table(DATA["arch_lm"], missing_label="ARCH-LM diagnostics are not available.")
        with diag_tabs[3]:
            render_table(DATA["distribution"], missing_label="Distribution summary is not available.")


def render_backtesting(filters: dict[str, Any]) -> None:
    page_header(
        "Backtesting",
        "Out-of-sample VaR evaluation using realized loss, Kupiec coverage, and Christoffersen independence tests.",
    )
    filters["model"] = "COMPARE"
    filters["model_label"] = "Compare"
    filters = _page_filter_controls("backtesting", filters, show_model=False)

    btc_df = DATA["btc"]
    risk_df = DATA["risk"]
    backtesting_df = RAW_DATA["backtesting"]
    confidence = filters["confidence"]
    selected_rows = _selected_backtest_rows(backtesting_df, filters["model"], confidence)
    warn_missing_many(missing_files(OUTPUT_DIR, ["risk", "backtesting", "model_rank", "price_demo"]))

    _render_historical_forecast_replay(DATA["price_demo"])
    realtime_backtesting_panel(btc_df, risk_df, filters["model"], confidence)

    st.subheader("Pass / Fail Status")
    for row in _rows_as_records(selected_rows):
        st.markdown(f"**{_model_label(row.get('model'))}**")
        col1, col2, col3 = st.columns(3)
        with col1:
            status_message("Coverage", _as_bool(row.get("coverage_pass_5pct")))
        with col2:
            status_message("Independence", _as_bool(row.get("independence_pass_5pct")))
        with col3:
            status_message("Conditional Coverage", _as_bool(row.get("conditional_coverage_pass_5pct")))

    st.caption(
        "Kupiec evaluates unconditional coverage, while Christoffersen evaluates breach independence. "
        "A p-value of at least 0.05 indicates no rejection at the 5% significance level."
    )

    col1, col2 = st.columns(2)
    with col1:
        render_table(
            _breach_events_table(risk_df, filters["model"], confidence),
            "Breach Event Dates",
            "No breach events are available for the selected filters.",
            height=320,
        )
    with col2:
        render_table(
            _comparison_table(RAW_DATA["model_rank"], confidence),
            "MS-GARCH vs SV Comparison",
            "Model comparison output is not available.",
            height=320,
        )

    render_table(
        backtesting_df,
        "Backtesting Summary Table",
        "Backtesting summary output is not available.",
    )


def render_forecast(filters: dict[str, Any]) -> None:
    page_header(
        "Forecast",
        "Next-day risk forecast and one-step-ahead price forecast.",
    )
    selected_model = _forecast_submit_controls()

    st.caption(
        "The price projection is shown as a one-step-ahead reference. The primary analysis remains volatility, "
        "VaR, CVaR, and out-of-sample backtesting."
    )

    warn_missing_many(missing_files(OUTPUT_DIR, ["next_day", "price_demo"]))
    if selected_model is None:
        st.info("Select a model, then press Forecast to generate the next-day forecast view.")
        return

    forecast_rows = _next_day_rows(RAW_DATA["next_day"], selected_model)
    realtime_forecast_panel(forecast_rows, DATA["price_demo"], selected_model)


def render_about() -> None:
    page_header("About", "Thesis scope, dataset, model structure, and evaluation design.")
    model_summary = RAW_DATA["model_summary"]
    if model_summary:
        validation = model_summary.get("data_validation", {})
        split = model_summary.get("split", {})
    else:
        validation = {}
        split = {}

    st.markdown(
        f"""
        <div class="about-grid">
            <div class="about-card about-card-primary">
                <div class="about-kicker">Thesis Profile</div>
                <div class="about-title">{escape(THESIS_TITLE)}</div>
                <div class="about-list">
                    {_about_row("Author", AUTHOR)}
                    {_about_row("Research Object", "Bitcoin BTCUSDT daily data")}
                    {_about_row("Data Source", "Binance BTCUSDT daily market data")}
                    {_about_row("Program Context", "Computer Science and Statistics")}
                </div>
            </div>
            <div class="about-card">
                <div class="about-kicker">Modeling Framework</div>
                <div class="about-list">
                    {_about_row("Variables", "Open, High, Low, Close, Volume, Log Return")}
                    {_about_row("Mean Filter", "ARMA")}
                    {_about_row("Volatility Models", "MS-GARCH and Stochastic Volatility")}
                    {_about_row("Risk Measures", "VaR and CVaR at 95% and 99% confidence levels")}
                    {_about_row("Evaluation", "Out-of-sample backtesting with Kupiec and Christoffersen tests")}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if model_summary:
        metric_grid(
            [
                {"label": "Sample Start", "value": fmt_date(validation.get("start"))},
                {"label": "Sample End", "value": fmt_date(validation.get("end"))},
                {"label": "Observations", "value": fmt_number(validation.get("n_rows"), 0)},
                {"label": "Training Rows", "value": fmt_number(split.get("train_n"), 0)},
                {"label": "Testing Rows", "value": fmt_number(split.get("test_n"), 0)},
                {"label": "Frequency", "value": "Daily"},
            ],
            columns_per_row=3,
        )
    else:
        st.warning("Model summary JSON is not available.")

    st.markdown(
        """
        <div class="about-card about-card-wide">
            <div class="about-kicker">Empirical Workflow</div>
            <div class="about-flow">
                <div class="about-step"><span>1</span><strong>Data Collection</strong><small>BTCUSDT daily OHLCV</small></div>
                <div class="about-step"><span>2</span><strong>Preprocessing</strong><small>cleaning and log return</small></div>
                <div class="about-step"><span>3</span><strong>Modeling</strong><small>ARMA, MS-GARCH, SV</small></div>
                <div class="about-step"><span>4</span><strong>Risk Measurement</strong><small>VaR and CVaR</small></div>
                <div class="about-step"><span>5</span><strong>Evaluation</strong><small>out-of-sample tests</small></div>
            </div>
        </div>
        <div class="about-scope">
            The empirical scope is limited to daily BTCUSDT observations and single-asset market risk measurement.
            The results are intended to evaluate volatility behavior, downside risk, and backtesting performance.
        </div>
        """,
        unsafe_allow_html=True,
    )


def _about_row(label: str, value: str) -> str:
    return (
        '<div class="about-row">'
        f'<div class="about-row-label">{escape(label)}</div>'
        f'<div class="about-row-value">{escape(value)}</div>'
        "</div>"
    )


def _latest_row(df: pd.DataFrame) -> pd.Series | None:
    if df.empty:
        return None
    clean = df.dropna(how="all")
    if clean.empty:
        return None
    return clean.iloc[-1]


def _value(row: pd.Series | None, column: str):
    if row is None or column not in row.index:
        return None
    return row.get(column)


def _latest_model_values(
    row: pd.Series | None,
    models: tuple[str, ...],
    column_template: str,
    percent: bool = False,
) -> str:
    if row is None:
        return "N/A"

    values: list[str] = []
    for model in models:
        value = _value(row, column_template.format(model=model))
        formatted = fmt_percent(value) if percent else fmt_number(value)
        if len(models) == 1:
            return formatted
        values.append(f"{_short_model_label(model)} {formatted}")
    return " | ".join(values) if values else "N/A"


def _latest_breach_status(row: pd.Series | None, models: tuple[str, ...], confidence: str) -> str:
    if row is None or "actual_loss" not in row.index:
        return "N/A"

    statuses: list[str] = []
    for model in models:
        var_col = f"{model}_VaR_{confidence}"
        if var_col not in row.index or is_missing(row[var_col]):
            continue
        breached = row["actual_loss"] > row[var_col]
        status = "Breach" if breached else "No Breach"
        if len(models) == 1:
            return status
        statuses.append(f"{_short_model_label(model)} {status}")
    return " | ".join(statuses) if statuses else "N/A"


def _daily_risk_table(risk_df: pd.DataFrame, model: str, confidence: str, n_rows: int = 30) -> pd.DataFrame:
    if risk_df.empty:
        return pd.DataFrame()

    models = _selected_models(model)
    columns = ["open_time", "actual_return", "actual_loss"]
    for model_key in models:
        columns.extend(
            [
                f"{model_key}_sigma",
                f"{model_key}_VaR_{confidence}",
                f"{model_key}_CVaR_{confidence}",
            ]
        )
    columns.append("MS_GARCH_p_high")

    available = [column for column in columns if column in risk_df.columns]
    if not available:
        return pd.DataFrame()

    table = risk_df[available].tail(n_rows).copy()
    for model_key in models:
        var_col = f"{model_key}_VaR_{confidence}"
        if {"actual_loss", var_col}.issubset(table.columns):
            breach_col = f"{model_key}_breach"
            table[breach_col] = table["actual_loss"] > table[var_col]
    return table.sort_values("open_time", ascending=False) if "open_time" in table.columns else table


def _selected_backtest_rows(df: pd.DataFrame, model: str, confidence: str) -> pd.DataFrame:
    if df.empty or not {"model", "confidence"}.issubset(df.columns):
        return pd.DataFrame()

    confidence_value = float(confidence) / 100
    model_mask = df["model"].astype(str).str.upper().isin(_selected_models(model))
    confidence_mask = pd.to_numeric(df["confidence"], errors="coerce").round(4) == round(confidence_value, 4)
    return df[model_mask & confidence_mask].copy()


def _backtesting_metrics(rows: pd.DataFrame) -> list[dict[str, str]]:
    if rows.empty:
        return [
            {"label": "Number of Observations", "value": "N/A"},
            {"label": "Expected Breaches", "value": "N/A"},
            {"label": "Breach Count", "value": "N/A"},
            {"label": "Breach Rate", "value": "N/A"},
            {"label": "Kupiec p-value", "value": "N/A"},
            {"label": "Christoffersen p-value", "value": "N/A"},
            {"label": "Coverage", "value": "N/A"},
            {"label": "Independence", "value": "N/A"},
        ]

    records = _rows_as_records(rows)
    return [
        {"label": "Number of Observations", "value": _combine_records(records, "n_obs", "number", 0)},
        {"label": "Expected Breaches", "value": _combine_records(records, "expected_breaches", "number", 2)},
        {"label": "Breach Count", "value": _combine_records(records, "breach_count", "number", 0)},
        {"label": "Breach Rate", "value": _combine_records(records, "breach_rate", "percent")},
        {"label": "Kupiec p-value", "value": _combine_records(records, "kupiec_pvalue", "number", 4)},
        {
            "label": "Christoffersen p-value",
            "value": _combine_records(records, "christoffersen_cc_pvalue", "number", 4),
        },
        {"label": "Coverage", "value": _combine_records(records, "coverage_pass_5pct", "status")},
        {"label": "Independence", "value": _combine_records(records, "independence_pass_5pct", "status")},
    ]


def _breach_events_table(risk_df: pd.DataFrame, model: str, confidence: str) -> pd.DataFrame:
    if risk_df.empty or not {"open_time", "actual_loss"}.issubset(risk_df.columns):
        return pd.DataFrame()

    events: list[pd.DataFrame] = []
    for model_key in _selected_models(model):
        var_col = f"{model_key}_VaR_{confidence}"
        if var_col not in risk_df.columns:
            continue
        breaches = risk_df[risk_df["actual_loss"] > risk_df[var_col]].copy()
        if breaches.empty:
            continue
        breaches["model"] = _model_label(model_key)
        breaches["var_threshold"] = breaches[var_col]
        breaches["excess_loss"] = breaches["actual_loss"] - breaches[var_col]
        events.append(breaches[["open_time", "model", "actual_loss", "var_threshold", "excess_loss"]])

    if not events:
        return pd.DataFrame()
    return pd.concat(events, ignore_index=True).sort_values("open_time", ascending=False)


def _comparison_table(df: pd.DataFrame, confidence: str) -> pd.DataFrame:
    if df.empty or "confidence" not in df.columns:
        return pd.DataFrame()

    confidence_value = float(confidence) / 100
    return df[pd.to_numeric(df["confidence"], errors="coerce").round(4) == round(confidence_value, 4)].copy()


def _overview_model_table(df: pd.DataFrame, model: str, confidence: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    table = _comparison_table(df, confidence) if "confidence" in df.columns else df.copy()
    if model != "COMPARE" and "model" in table.columns:
        table = table[table["model"].astype(str).str.upper() == model].copy()
    return table


def _render_historical_forecast_replay(price_demo_df: pd.DataFrame) -> None:
    st.subheader("Historical Forecast Simulation")

    required = {"open_time", "close_prev", "close_actual", "close_pred_ms", "close_pred_sv"}
    if price_demo_df.empty or not required.issubset(price_demo_df.columns):
        st.warning("Historical forecast simulation data is not available.")
        return

    replay_df = price_demo_df.dropna(subset=["open_time"]).sort_values("open_time").copy()
    replay_df["open_time"] = pd.to_datetime(replay_df["open_time"], errors="coerce", utc=True)
    replay_df = replay_df.dropna(subset=["open_time"]).copy()
    if replay_df.empty:
        st.warning("Historical forecast simulation dates are not available.")
        return

    with st.container(border=True):
        st.markdown("**Simulation Controls**")
        control_left, control_right = st.columns(2)
        with control_left:
            horizon_label = st.radio(
                "Select Horizon",
                options=["1D", "3D", "7D"],
                index=0,
                key="backtesting_simulation_horizon",
                horizontal=True,
                width="stretch",
            )
            st.caption("Options: 1D, 3D, 7D")

        horizon_label = horizon_label or "1D"
        horizon_days = int(horizon_label.removesuffix("D"))
        origin_dates = _valid_simulation_origin_dates(replay_df, horizon_days)
        if not origin_dates:
            st.warning("No historical dates are available for the selected horizon.")
            return

        with control_right:
            selected_origin_input = st.date_input(
                "Select Start Date",
                value=origin_dates[-1],
                min_value=origin_dates[0],
                max_value=origin_dates[-1],
                key=f"backtesting_simulation_start_date_picker_{horizon_days}",
                help=(
                    "Available range: "
                    f"{pd.Timestamp(origin_dates[0]).strftime('%Y/%m/%d')} to "
                    f"{pd.Timestamp(origin_dates[-1]).strftime('%Y/%m/%d')}."
                ),
                format="YYYY/MM/DD",
                width="stretch",
            )
            selected_origin = selected_origin_input
            if selected_origin not in origin_dates:
                selected_origin = min(
                    origin_dates,
                    key=lambda date: abs(pd.Timestamp(date) - pd.Timestamp(selected_origin_input)),
                )
                st.caption(f"Nearest available simulation date: {pd.Timestamp(selected_origin).strftime('%Y/%m/%d')}")
            else:
                st.caption("Historical simulation start date")

    replay_rows = _historical_simulation_rows(replay_df, selected_origin, horizon_days)
    if replay_rows.empty:
        st.warning("Selected date does not have enough historical forecast data for this horizon.")
        return

    _render_historical_replay_summary(replay_rows, horizon_label)

    render_plotly(charts.historical_forecast_replay_chart(replay_rows))
    render_table(
        replay_rows[
            [
                "model_label",
                "horizon",
                "origin_date",
                "target_date",
                "start_close",
                "predicted_close",
                "actual_close",
                "prediction_error",
                "prediction_error_pct",
                "actual_return",
                "actual_loss",
            ]
        ],
        "Simulation Detail Table",
        "Simulation detail is not available.",
        height=260,
    )


def _render_historical_replay_summary(replay_rows: pd.DataFrame, horizon_label: str) -> None:
    first = replay_rows.iloc[0]
    timeline = [
        ("Start Date", fmt_date(first["origin_date"]), "Simulation start"),
        ("Target Date", fmt_date(first["target_date"]), f"Horizon {horizon_label}"),
        ("Start Price", fmt_currency(first["start_close"]), "Actual start close"),
        ("Actual Price", fmt_currency(first["actual_close"]), "Observed target close"),
    ]

    timeline_html = "".join(
        (
            '<div class="simulation-tile">'
            f'<div class="simulation-label">{escape(label)}</div>'
            f'<div class="simulation-value">{escape(value)}</div>'
            f'<div class="simulation-caption">{escape(caption)}</div>'
            "</div>"
        )
        for label, value, caption in timeline
    )

    actual_html = (
        '<section class="simulation-panel simulation-accent-blue">'
        '<div class="simulation-panel-title">'
        "<span>Actual Outcome</span>"
        '<span class="simulation-pill">REALIZED</span>'
        "</div>"
        f'<div class="simulation-panel-main">{escape(fmt_currency(first["actual_close"]))}</div>'
        '<div class="simulation-mini-grid">'
        '<div class="simulation-mini">'
        '<div class="simulation-label">Actual Return</div>'
        f'<div class="simulation-value">{escape(fmt_percent(first["actual_return"]))}</div>'
        "</div>"
        '<div class="simulation-mini">'
        '<div class="simulation-label">Actual Loss</div>'
        f'<div class="simulation-value">{escape(fmt_percent(first["actual_loss"]))}</div>'
        "</div>"
        "</div>"
        "</section>"
    )

    model_panels: list[str] = []
    for _, row in replay_rows.iterrows():
        accent = "cyan" if row["model"] == "MS_GARCH" else "purple"
        model_panels.append(
            (
                f'<section class="simulation-panel simulation-accent-{accent}">'
                '<div class="simulation-panel-title">'
                f'<span>{escape(str(row["model_label"]))}</span>'
                '<span class="simulation-pill">MODEL</span>'
                "</div>"
                f'<div class="simulation-panel-main">{escape(fmt_currency(row["predicted_close"]))}</div>'
                '<div class="simulation-mini-grid">'
                '<div class="simulation-mini">'
                '<div class="simulation-label">Prediction Error</div>'
                f'<div class="simulation-value">{escape(fmt_currency(row["prediction_error"]))}</div>'
                "</div>"
                '<div class="simulation-mini">'
                '<div class="simulation-label">Error Percentage</div>'
                f'<div class="simulation-value">{escape(fmt_percent(row["prediction_error_pct"]))}</div>'
                "</div>"
                "</div>"
                "</section>"
            )
        )

    st.markdown(
        '<div class="simulation-summary">'
        f'<div class="simulation-timeline">{timeline_html}</div>'
        f'<div class="simulation-comparison">{actual_html}{"".join(model_panels)}</div>'
        "</div>",
        unsafe_allow_html=True,
    )


def _valid_simulation_origin_dates(price_demo_df: pd.DataFrame, horizon_days: int) -> list[Any]:
    close_by_date = _historical_close_by_date(price_demo_df)
    target_dates = set(price_demo_df["open_time"].dt.date)
    origin_dates = sorted(close_by_date)
    valid: list[Any] = []
    for origin_date in origin_dates:
        target_date = (pd.Timestamp(origin_date) + pd.Timedelta(days=horizon_days)).date()
        required_targets = {
            (pd.Timestamp(origin_date) + pd.Timedelta(days=step)).date()
            for step in range(1, horizon_days + 1)
        }
        if target_date in close_by_date and required_targets.issubset(target_dates):
            valid.append(origin_date)
    return valid


def _historical_simulation_rows(
    price_demo_df: pd.DataFrame,
    origin_date: Any,
    horizon_days: int,
) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    close_by_date = _historical_close_by_date(price_demo_df)
    row_by_target = {
        pd.Timestamp(row["open_time"]).date(): row
        for _, row in price_demo_df.iterrows()
        if not is_missing(row.get("open_time"))
    }
    origin_date = pd.Timestamp(origin_date).date()
    target_date = (pd.Timestamp(origin_date) + pd.Timedelta(days=horizon_days)).date()
    start_close = close_by_date.get(origin_date)
    actual_close = close_by_date.get(target_date)
    if is_missing(start_close) or is_missing(actual_close):
        return pd.DataFrame()

    actual_return = math.log(float(actual_close) / float(start_close))
    actual_loss = -actual_return

    for model_key in MODEL_KEYS:
        suffix = "ms" if model_key == "MS_GARCH" else "sv"
        predicted_close = float(start_close)
        missing_step = False
        for step in range(1, horizon_days + 1):
            step_date = (pd.Timestamp(origin_date) + pd.Timedelta(days=step)).date()
            step_row = row_by_target.get(step_date)
            if step_row is None or is_missing(step_row.get("close_prev")) or is_missing(step_row.get(f"close_pred_{suffix}")):
                missing_step = True
                break
            predicted_factor = float(step_row.get(f"close_pred_{suffix}")) / float(step_row.get("close_prev"))
            predicted_close *= predicted_factor
        if missing_step:
            continue

        prediction_error = float(actual_close) - predicted_close
        prediction_error_pct = prediction_error / float(actual_close) if float(actual_close) != 0 else None

        records.append(
            {
                "model": model_key,
                "model_label": _model_label(model_key),
                "horizon": f"{horizon_days}D",
                "origin_date": pd.Timestamp(origin_date, tz="UTC"),
                "target_date": pd.Timestamp(target_date, tz="UTC"),
                "start_close": start_close,
                "predicted_close": predicted_close,
                "actual_close": actual_close,
                "prediction_error": prediction_error,
                "prediction_error_pct": prediction_error_pct,
                "actual_return": actual_return,
                "actual_loss": actual_loss,
            }
        )

    return pd.DataFrame(records)


def _historical_close_by_date(price_demo_df: pd.DataFrame) -> dict[Any, float]:
    close_by_date: dict[Any, float] = {}
    for _, row in price_demo_df.iterrows():
        target_date = pd.Timestamp(row["open_time"]).date()
        origin_date = (pd.Timestamp(row["open_time"]) - pd.Timedelta(days=1)).date()
        if not is_missing(row.get("close_prev")) and origin_date not in close_by_date:
            close_by_date[origin_date] = float(row.get("close_prev"))
        if not is_missing(row.get("close_actual")):
            close_by_date[target_date] = float(row.get("close_actual"))
    return close_by_date


def _next_day_rows(df: pd.DataFrame, model: str) -> pd.DataFrame:
    if df.empty or "model" not in df.columns:
        return pd.DataFrame()
    if model == "COMPARE":
        return df[df["model"].astype(str).str.upper().isin(MODEL_KEYS)].copy()
    return df[df["model"].astype(str).str.upper() == model].copy()


def _render_forecast_cards(rows: pd.DataFrame) -> None:
    if rows.empty:
        st.warning("Next-day forecast rows are not available.")
        return

    for _, row in rows.iterrows():
        st.subheader(_model_label(row.get("model")))
        cols = st.columns(4)
        card_values = [
            ("Forecast Date", fmt_date(row.get("forecast_date")), None),
            ("Last Close", fmt_currency(row.get("last_close")), None),
            ("Predicted Close", fmt_currency(_predicted_close(row)), "Median simulation if available."),
            ("VaR 95", fmt_percent(row.get("VaR_95")), None),
            ("CVaR 95", fmt_percent(row.get("CVaR_95")), None),
            ("VaR 99", fmt_percent(row.get("VaR_99")), None),
            ("CVaR 99", fmt_percent(row.get("CVaR_99")), None),
            ("High Volatility Probability", fmt_percent(row.get("p_high_state")), "MS-GARCH only if available."),
        ]
        for idx, (label, value, caption) in enumerate(card_values):
            with cols[idx % 4]:
                info_card(label, value, caption)


def _predicted_close(row: pd.Series):
    if "predicted_close_median_sim" in row.index and not is_missing(row.get("predicted_close_median_sim")):
        return row.get("predicted_close_median_sim")
    if "predicted_close_mu" in row.index and not is_missing(row.get("predicted_close_mu")):
        return row.get("predicted_close_mu")
    return None


def _preferred_ms_probability() -> pd.DataFrame:
    if not DATA["ms_smoothed_prob"].empty:
        return DATA["ms_smoothed_prob"]
    return DATA["ms_filtered_prob"]


def _selected_models(model: str) -> tuple[str, ...]:
    return MODEL_KEYS if model == "COMPARE" else (model,)


def _rows_as_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    return df.to_dict("records") if not df.empty else []


def _combine_records(records: list[dict[str, Any]], key: str, kind: str, digits: int = 4) -> str:
    values: list[str] = []
    for record in records:
        model = _short_model_label(record.get("model"))
        value = record.get(key)
        if kind == "percent":
            formatted = fmt_percent(value)
        elif kind == "status":
            formatted = format_pass_fail(value)
        else:
            formatted = fmt_number(value, digits)
        values.append(formatted if len(records) == 1 else f"{model} {formatted}")
    return " | ".join(values) if values else "N/A"


def _as_bool(value) -> bool | None:
    if is_missing(value):
        return None
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "pass", "passed"}:
            return True
        if lowered in {"false", "fail", "failed"}:
            return False
    return bool(value)


def _model_label(model: Any) -> str:
    return MODEL_LABELS.get(str(model), str(model))


def _short_model_label(model: Any) -> str:
    model_key = str(model)
    if model_key == "MS_GARCH":
        return "MS"
    if model_key == "SV":
        return "SV"
    return _model_label(model_key)


def _render_price_chart_section(price_chart_df: pd.DataFrame, current_timeframe: str) -> str:
    with st.container(border=True):
        st.markdown("<div class='price-chart-title'>BTCUSDT Close Price</div>", unsafe_allow_html=True)
        range_col, refresh_col = st.columns([0.78, 0.22], gap="medium", vertical_alignment="center")
        with range_col:
            timeframe_options = ["1D", "7D", "30D", "90D", "1Y", "All"]
            timeframe = st.radio(
                "BTC Price Range",
                options=timeframe_options,
                index=timeframe_options.index(current_timeframe) if current_timeframe in timeframe_options else 2,
                key="dashboard_price_timeframe",
                horizontal=True,
                label_visibility="collapsed",
                width="stretch",
            )
        with refresh_col:
            if st.button("Refresh", width="stretch"):
                fetch_price_klines.clear()
                st.rerun()

        timeframe = timeframe or current_timeframe or "30D"
        render_plotly(charts.btc_close_chart(price_chart_df, timeframe))
    return timeframe


def _price_chart_data(base_df: pd.DataFrame, realtime_df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    if timeframe == "All":
        return merge_daily_realtime(base_df, realtime_df) if not realtime_df.empty else base_df

    if not realtime_df.empty:
        return realtime_df

    if base_df.empty:
        return pd.DataFrame()

    fallback_rows = {
        "1D": 2,
        "7D": 7,
        "30D": 30,
        "90D": 90,
        "1Y": 365,
    }.get(timeframe, 30)
    return base_df.tail(fallback_rows).copy()


def _format_live_timestamp(value: Any) -> str | None:
    if is_missing(value):
        return None
    parsed = pd.to_datetime(value, errors="coerce", utc=True)
    if pd.isna(parsed):
        return None
    return parsed.strftime("%Y-%m-%d %H:%M UTC")


def _first_available(*values: Any) -> Any:
    for value in values:
        if not is_missing(value):
            return value
    return None


def _forecast_submit_controls() -> str | None:
    model_options = {
        "MS-GARCH": "MS_GARCH",
        "Stochastic Volatility": "SV",
        "Both Models": "COMPARE",
    }
    saved_label = st.session_state.get("forecast_submitted_model_label", "MS-GARCH")

    with st.container(border=True):
        st.markdown("**Forecast Setup**")
        with st.form("forecast_setup_form", clear_on_submit=False):
            model_label = st.radio(
                "Select Model",
                options=list(model_options.keys()),
                index=list(model_options.keys()).index(saved_label) if saved_label in model_options else 0,
                horizontal=True,
                key="forecast_model_choice",
                width="stretch",
            )
            submitted = st.form_submit_button("Forecast", width="stretch")

    if submitted:
        st.session_state["forecast_has_run"] = True
        st.session_state["forecast_submitted_model_label"] = model_label or "MS-GARCH"

    if not st.session_state.get("forecast_has_run", False):
        return None

    selected_label = st.session_state.get("forecast_submitted_model_label", "MS-GARCH")
    return model_options.get(selected_label, "MS_GARCH")


def _page_filter_controls(
    page_key: str,
    base_filters: dict[str, Any],
    show_model: bool = True,
    show_confidence: bool = True,
) -> dict[str, Any]:
    filters = base_filters.copy()
    controls = st.container(border=True)

    with controls:
        st.markdown("**View Controls**")
        columns = st.columns(2 if show_model and show_confidence else 1)

        if show_model:
            with columns[0]:
                model_options = list(MODEL_OPTIONS.keys())
                model_label = st.radio(
                    "Model",
                    options=model_options,
                    index=model_options.index(filters.get("model_label", "MS-GARCH"))
                    if filters.get("model_label", "MS-GARCH") in model_options
                    else 0,
                    key=f"{page_key}_model",
                    horizontal=True,
                    width="stretch",
                )
            model_label = model_label or "MS-GARCH"
            filters["model"] = MODEL_OPTIONS[model_label]
            filters["model_label"] = model_label

        if show_confidence:
            with columns[-1]:
                confidence_options = list(CONFIDENCE_OPTIONS.keys())
                confidence_label = st.radio(
                    "Confidence Level",
                    options=confidence_options,
                    index=confidence_options.index(filters.get("confidence_label", "95%"))
                    if filters.get("confidence_label", "95%") in confidence_options
                    else 0,
                    key=f"{page_key}_confidence",
                    horizontal=True,
                    width="stretch",
                )
            confidence_label = confidence_label or "95%"
            filters["confidence"] = CONFIDENCE_OPTIONS[confidence_label]
            filters["confidence_label"] = confidence_label

    st.write("")
    return filters


def main() -> None:
    global DATA, OUTPUT_DIR, RAW_DATA

    st.set_page_config(
        page_title=APP_TITLE,
        layout="wide",
    )

    if "dark_theme_enabled" not in st.session_state:
        st.session_state["dark_theme_enabled"] = False

    set_global_styles()

    OUTPUT_DIR, _output_notes = resolve_output_dir()
    RAW_DATA = load_outputs(OUTPUT_DIR)

    date_min, date_max = available_date_bounds(RAW_DATA)
    DATA = RAW_DATA

    with st.sidebar:
        sidebar_title(APP_TITLE)
        page = st.radio("Navigation", PAGES, label_visibility="collapsed")
        st.markdown("<div class='sidebar-footer-spacer'></div>", unsafe_allow_html=True)
        st.toggle("Dark theme", key="dark_theme_enabled")

    filters = {
        "start": date_min,
        "end": date_max,
    }

    if page == "Dashboard":
        render_dashboard(filters)
    elif page == "Models & Diagnostics":
        render_models_diagnostics(filters)
    elif page == "Backtesting":
        render_backtesting(filters)
    elif page == "Forecast":
        render_forecast(filters)
    elif page == "About":
        render_about()


if __name__ == "__main__":
    main()
