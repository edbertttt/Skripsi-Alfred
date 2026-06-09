from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.constants import MODEL_KEYS, MODEL_LABELS


COLOR_PRICE = "#2f5fda"
COLOR_RETURN = "#5b677a"
COLOR_MS = "#0f7f8f"
COLOR_SV = "#6d5bd0"
COLOR_VAR = "#c24150"
COLOR_CVAR = "#b86b0b"
COLOR_BREACH = "#b4234a"
COLOR_OK = "#168a69"
COLOR_AMBER = "#b86b0b"
COLOR_MUTED = "#98a2b3"

MODEL_COLORS = {
    "MS_GARCH": COLOR_MS,
    "SV": COLOR_SV,
}


def empty_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font={"size": 14, "color": COLOR_RETURN},
    )
    _apply_layout(fig, title="")
    return fig


def btc_close_chart(df: pd.DataFrame, timeframe: str = "30D") -> go.Figure:
    required = {"open_time", "close"}
    if df.empty or not required.issubset(df.columns):
        return empty_figure("BTC close price data is not available.")

    use_log_scale = timeframe == "All"
    y_title = "Close Price (USDT, log scale)" if use_log_scale else "Close Price (USDT)"

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["open_time"],
            y=df["close"],
            mode="lines",
            name="BTC Close",
            line={"color": COLOR_PRICE, "width": 2},
            fill="tozeroy",
            fillcolor="rgba(47, 95, 218, 0.10)",
            hovertemplate="%{x|%Y-%m-%d}<br>Close: %{y:,.2f} USDT<extra></extra>",
        )
    )
    _apply_layout(fig, f"BTCUSDT Close Price ({timeframe})", y_title)
    fig.update_xaxes(
        rangeslider={
            "visible": True,
            "thickness": 0.055,
            "bgcolor": "rgba(148, 163, 184, 0.08)",
            "bordercolor": "rgba(148, 163, 184, 0.22)",
            "borderwidth": 1,
        },
    )
    fig.update_yaxes(type="log" if use_log_scale else "linear", tickprefix="$")
    fig.update_layout(height=500, margin={"l": 24, "r": 24, "t": 58, "b": 72}, showlegend=False)
    return fig


def log_return_chart(df: pd.DataFrame) -> go.Figure:
    required = {"open_time", "ret_log"}
    if df.empty or not required.issubset(df.columns):
        return empty_figure("Log return data is not available.")

    fig = go.Figure()
    fig.add_hline(y=0, line_color=COLOR_MUTED, line_width=1)
    fig.add_trace(
        go.Scatter(
            x=df["open_time"],
            y=df["ret_log"],
            mode="lines",
            name="Log Return",
            line={"color": COLOR_RETURN, "width": 1.4},
            hovertemplate="%{x|%Y-%m-%d}<br>Log Return: %{y:.4%}<extra></extra>",
        )
    )
    _apply_layout(fig, "Daily Log Return", "Log Return")
    fig.update_yaxes(tickformat=".1%")
    return fig


def volatility_chart(
    btc_df: pd.DataFrame,
    risk_df: pd.DataFrame,
    model: str,
) -> go.Figure:
    fig = go.Figure()
    has_trace = False

    if not btc_df.empty and {"open_time", "rolling_vol_30d"}.issubset(btc_df.columns):
        fig.add_trace(
            go.Scatter(
                x=btc_df["open_time"],
                y=btc_df["rolling_vol_30d"],
                mode="lines",
                name="30D Realized Volatility",
                line={"color": COLOR_MUTED, "width": 1.5, "dash": "dot"},
                hovertemplate="%{x|%Y-%m-%d}<br>Realized Vol: %{y:.4%}<extra></extra>",
            )
        )
        has_trace = True

    for model_key in _selected_models(model):
        sigma_col = f"{model_key}_sigma"
        if not risk_df.empty and {"open_time", sigma_col}.issubset(risk_df.columns):
            fig.add_trace(
                go.Scatter(
                    x=risk_df["open_time"],
                    y=risk_df[sigma_col],
                    mode="lines",
                    name=f"{_model_label(model_key)} Sigma",
                    line={"color": MODEL_COLORS.get(model_key, COLOR_MS), "width": 2},
                    hovertemplate="%{x|%Y-%m-%d}<br>Sigma: %{y:.4%}<extra></extra>",
                )
            )
            has_trace = True

    if not has_trace:
        return empty_figure("Volatility data is not available.")

    _apply_layout(fig, "Volatility Comparison", "Volatility / Sigma")
    fig.update_yaxes(tickformat=".1%")
    return fig


def realized_loss_vs_var_chart(
    risk_df: pd.DataFrame,
    model: str,
    confidence: str,
) -> go.Figure:
    if risk_df.empty or not {"open_time", "actual_loss"}.issubset(risk_df.columns):
        return empty_figure("Realized loss and VaR data is not available.")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=risk_df["open_time"],
            y=risk_df["actual_loss"],
            mode="lines",
            name="Realized Loss",
            line={"color": COLOR_RETURN, "width": 1.4},
            hovertemplate="%{x|%Y-%m-%d}<br>Loss: %{y:.4%}<extra></extra>",
        )
    )

    has_threshold = False
    for model_key in _selected_models(model):
        var_col = f"{model_key}_VaR_{confidence}"
        cvar_col = f"{model_key}_CVaR_{confidence}"
        if var_col not in risk_df.columns:
            continue
        color = MODEL_COLORS.get(model_key, COLOR_VAR)
        fig.add_trace(
            go.Scatter(
                x=risk_df["open_time"],
                y=risk_df[var_col],
                mode="lines",
                name=f"{_model_label(model_key)} VaR {confidence}%",
                line={"color": color, "width": 2},
                hovertemplate="%{x|%Y-%m-%d}<br>VaR: %{y:.4%}<extra></extra>",
            )
        )
        has_threshold = True

        if model != "COMPARE" and cvar_col in risk_df.columns:
            fig.add_trace(
                go.Scatter(
                    x=risk_df["open_time"],
                    y=risk_df[cvar_col],
                    mode="lines",
                    name=f"{_model_label(model_key)} CVaR {confidence}%",
                    line={"color": COLOR_CVAR, "width": 1.8, "dash": "dot"},
                    hovertemplate="%{x|%Y-%m-%d}<br>CVaR: %{y:.4%}<extra></extra>",
                )
            )

        breach_df = _breach_rows(risk_df, model_key, confidence)
        if not breach_df.empty:
            fig.add_trace(
                go.Scatter(
                    x=breach_df["open_time"],
                    y=breach_df["actual_loss"],
                    mode="markers",
                    name=f"{_model_label(model_key)} Breach",
                    marker={"color": COLOR_BREACH, "size": 7, "symbol": "x"},
                    hovertemplate="%{x|%Y-%m-%d}<br>Breach Loss: %{y:.4%}<extra></extra>",
                )
            )

    if not has_threshold:
        return empty_figure("Selected VaR columns are not available.")

    _apply_layout(fig, f"Realized Loss vs VaR {confidence}%", "Loss / Risk Threshold")
    fig.update_yaxes(tickformat=".1%")
    return fig


def breach_event_chart(
    risk_df: pd.DataFrame,
    model: str,
    confidence: str,
) -> go.Figure:
    if risk_df.empty or not {"open_time", "actual_loss"}.issubset(risk_df.columns):
        return empty_figure("Breach event data is not available.")

    fig = go.Figure()
    has_trace = False
    for model_key in _selected_models(model):
        var_col = f"{model_key}_VaR_{confidence}"
        if var_col not in risk_df.columns:
            continue
        breach = (risk_df["actual_loss"] > risk_df[var_col]).astype(int)
        fig.add_trace(
            go.Bar(
                x=risk_df["open_time"],
                y=breach,
                name=f"{_model_label(model_key)} Breach",
                marker_color=np.where(breach == 1, MODEL_COLORS.get(model_key, COLOR_BREACH), "rgba(148, 163, 184, 0.22)"),
                hovertemplate="%{x|%Y-%m-%d}<br>Breach: %{y}<extra></extra>",
            )
        )
        has_trace = True

    if not has_trace:
        return empty_figure("Selected breach columns are not available.")

    _apply_layout(fig, f"VaR Breach Events {confidence}%", "Breach Indicator")
    fig.update_yaxes(tickmode="array", tickvals=[0, 1], range=[0, 1.15])
    fig.update_layout(barmode="overlay" if model == "COMPARE" else "relative")
    return fig


def high_vol_probability_chart(prob_df: pd.DataFrame, risk_df: pd.DataFrame | None = None) -> go.Figure:
    if not prob_df.empty and {"open_time", "p_high_vol"}.issubset(prob_df.columns):
        df = prob_df
        y_col = "p_high_vol"
    elif risk_df is not None and not risk_df.empty and {"open_time", "MS_GARCH_p_high"}.issubset(risk_df.columns):
        df = risk_df
        y_col = "MS_GARCH_p_high"
    else:
        return empty_figure("High volatility probability is not available.")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["open_time"],
            y=df[y_col],
            mode="lines",
            name="High Volatility State Probability",
            line={"color": COLOR_AMBER, "width": 2},
            fill="tozeroy",
            fillcolor="rgba(184, 107, 11, 0.12)",
            hovertemplate="%{x|%Y-%m-%d}<br>Probability: %{y:.2%}<extra></extra>",
        )
    )
    _apply_layout(fig, "MS-GARCH High Volatility State Probability", "Probability")
    fig.update_yaxes(tickformat=".0%", range=[0, 1])
    return fig


def sv_latent_volatility_chart(df: pd.DataFrame) -> go.Figure:
    required = {"open_time", "sigma_mean"}
    if df.empty or not required.issubset(df.columns):
        return empty_figure("SV latent volatility data is not available.")

    fig = go.Figure()
    if {"sigma_q025", "sigma_q975"}.issubset(df.columns):
        fig.add_trace(
            go.Scatter(
                x=df["open_time"],
                y=df["sigma_q975"],
                mode="lines",
                name="97.5% Interval",
                line={"color": "rgba(109, 91, 208, 0)", "width": 0},
                showlegend=False,
                hoverinfo="skip",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df["open_time"],
                y=df["sigma_q025"],
                mode="lines",
                name="95% Credible Interval",
                fill="tonexty",
                fillcolor="rgba(109, 91, 208, 0.14)",
                line={"color": "rgba(109, 91, 208, 0)", "width": 0},
                hovertemplate="%{x|%Y-%m-%d}<br>Lower: %{y:.4%}<extra></extra>",
            )
        )

    fig.add_trace(
        go.Scatter(
            x=df["open_time"],
            y=df["sigma_mean"],
            mode="lines",
            name="Posterior Mean Sigma",
            line={"color": COLOR_SV, "width": 2},
            hovertemplate="%{x|%Y-%m-%d}<br>Sigma: %{y:.4%}<extra></extra>",
        )
    )
    _apply_layout(fig, "SV Latent Volatility", "Sigma")
    fig.update_yaxes(tickformat=".1%")
    return fig


def ms_state_volatility_chart(df: pd.DataFrame) -> go.Figure:
    required = {"open_time", "sigma_low_vol", "sigma_high_vol"}
    if df.empty or not required.issubset(df.columns):
        return empty_figure("MS-GARCH state volatility data is not available.")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["open_time"],
            y=df["sigma_low_vol"],
            mode="lines",
            name="Low Volatility State",
            line={"color": COLOR_OK, "width": 1.8},
            hovertemplate="%{x|%Y-%m-%d}<br>Low State Sigma: %{y:.4%}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["open_time"],
            y=df["sigma_high_vol"],
            mode="lines",
            name="High Volatility State",
            line={"color": COLOR_VAR, "width": 1.8},
            hovertemplate="%{x|%Y-%m-%d}<br>High State Sigma: %{y:.4%}<extra></extra>",
        )
    )
    _apply_layout(fig, "MS-GARCH State Volatility", "Sigma")
    fig.update_yaxes(tickformat=".1%")
    return fig


def price_forecast_demo_chart(df: pd.DataFrame, model: str) -> go.Figure:
    required = {"open_time", "close_actual"}
    if df.empty or not required.issubset(df.columns):
        return empty_figure("Price forecast data is not available.")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["open_time"],
            y=df["close_actual"],
            mode="lines",
            name="Actual Close",
            line={"color": COLOR_PRICE, "width": 2},
            hovertemplate="%{x|%Y-%m-%d}<br>Actual: %{y:,.2f} USDT<extra></extra>",
        )
    )

    for model_key in _selected_models(model):
        suffix = "ms" if model_key == "MS_GARCH" else "sv"
        pred_col = f"close_pred_{suffix}"
        lo_col = f"close_pred_{suffix}_lo95"
        hi_col = f"close_pred_{suffix}_hi95"
        color = MODEL_COLORS.get(model_key, COLOR_AMBER)

        if {pred_col, lo_col, hi_col}.issubset(df.columns):
            fig.add_trace(
                go.Scatter(
                    x=df["open_time"],
                    y=df[hi_col],
                    mode="lines",
                    name=f"{_model_label(model_key)} Upper 95%",
                    line={"color": "rgba(184, 107, 11, 0)", "width": 0},
                    showlegend=False,
                    hoverinfo="skip",
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=df["open_time"],
                    y=df[lo_col],
                    mode="lines",
                    name=f"{_model_label(model_key)} 95% Interval",
                    fill="tonexty",
                    fillcolor=_interval_fill(model_key),
                    line={"color": "rgba(184, 107, 11, 0)", "width": 0},
                    hovertemplate="%{x|%Y-%m-%d}<br>Lower: %{y:,.2f} USDT<extra></extra>",
                )
            )
        if pred_col in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df["open_time"],
                    y=df[pred_col],
                    mode="lines",
                    name=f"{_model_label(model_key)} Predicted Close",
                    line={"color": color, "width": 2},
                    hovertemplate="%{x|%Y-%m-%d}<br>Predicted: %{y:,.2f} USDT<extra></extra>",
                )
            )

    _apply_layout(fig, "One-Step-Ahead Price Forecast", "Close Price (USDT)")
    return fig


def historical_forecast_replay_chart(df: pd.DataFrame) -> go.Figure:
    required = {"model", "model_label", "start_close", "predicted_close", "actual_close", "horizon"}
    if df.empty or not required.issubset(df.columns):
        return empty_figure("Historical forecast simulation data is not available.")

    first_row = df.iloc[0]
    horizon = str(first_row.get("horizon", ""))
    x_values = ["Start<br>Price", "Actual<br>Price"] + [f"{label}<br>Prediction" for label in df["model_label"]]
    y_values = [first_row.get("start_close"), first_row.get("actual_close")] + list(df["predicted_close"])
    colors = [COLOR_MUTED, COLOR_PRICE] + [
        MODEL_COLORS.get(str(model), COLOR_MS) for model in df["model"]
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=x_values,
            y=y_values,
            marker_color=colors,
            text=[f"${value:,.2f}" if pd.notna(value) else "N/A" for value in y_values],
            textposition="outside",
            hovertemplate="%{x}<br>Price: %{y:,.2f} USDT<extra></extra>",
            name="Price",
        )
    )

    _apply_layout(fig, f"Historical {horizon} Forecast Simulation", "BTC Close Price (USDT)")
    fig.update_yaxes(tickprefix="$")
    fig.update_layout(height=430, showlegend=False, margin={"l": 36, "r": 22, "t": 70, "b": 92})
    return fig


def _apply_layout(fig: go.Figure, title: str, y_title: str | None = None) -> None:
    fig.update_layout(
        template=None,
        title={"text": title, "x": 0.01, "xanchor": "left", "font": {"size": 17}},
        height=460,
        margin={"l": 28, "r": 22, "t": 70, "b": 118},
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": -0.25,
            "xanchor": "left",
            "x": 0,
            "font": {"size": 12},
        },
        font={"family": "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"},
    )
    fig.update_xaxes(showgrid=False, title=None, automargin=True)
    fig.update_yaxes(
        title=y_title,
        gridcolor="rgba(148, 163, 184, 0.22)",
        zerolinecolor="rgba(148, 163, 184, 0.45)",
        automargin=True,
    )


def _selected_models(model: str) -> tuple[str, ...]:
    return MODEL_KEYS if model == "COMPARE" else (model,)


def _model_label(model: str) -> str:
    return MODEL_LABELS.get(model, model)


def _breach_rows(risk_df: pd.DataFrame, model: str, confidence: str) -> pd.DataFrame:
    var_col = f"{model}_VaR_{confidence}"
    required = {"open_time", "actual_loss", var_col}
    if risk_df.empty or not required.issubset(risk_df.columns):
        return pd.DataFrame()
    return risk_df[risk_df["actual_loss"] > risk_df[var_col]].copy()


def _interval_fill(model: str) -> str:
    if model == "MS_GARCH":
        return "rgba(15, 127, 143, 0.12)"
    return "rgba(109, 91, 208, 0.10)"
