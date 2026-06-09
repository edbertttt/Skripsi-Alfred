from __future__ import annotations

from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APP_DIR.parent

APP_TITLE = "BitRisk"
THESIS_TITLE = (
    "Bitcoin Volatility and Risk Modeling via Markov-Switching GARCH and "
    "Stochastic Volatility: VaR and CVaR Analysis"
)
AUTHOR = "Alfred Edbert Yunanto"

PAGES = [
    "Dashboard",
    "Models & Diagnostics",
    "Backtesting",
    "Forecast",
    "About",
]

MODEL_OPTIONS = {
    "MS-GARCH": "MS_GARCH",
    "Stochastic Volatility": "SV",
    "Compare": "COMPARE",
}

MODEL_LABELS = {
    "MS_GARCH": "MS-GARCH",
    "SV": "Stochastic Volatility",
    "COMPARE": "Compare",
}

MODEL_KEYS = ("MS_GARCH", "SV")
CONFIDENCE_OPTIONS = {"95%": "95", "99%": "99"}

OUTPUT_DIR_NAMES = ("outputs",)
FALLBACK_OUTPUT_DIR_NAMES = ("outputs_optimized_notebook",)

CSV_FILES = {
    "btc": "btc_preprocessed_optimized.csv",
    "btc_train": "btc_train_optimized.csv",
    "btc_test": "btc_test_optimized.csv",
    "risk": "oos_risk_forecasts.csv",
    "backtesting": "backtesting_summary.csv",
    "next_day": "next_day_risk_forecast.csv",
    "price_demo": "price_forecast_demo.csv",
    "model_rank": "model_comparison_rank.csv",
    "best_model": "best_model_by_confidence.csv",
    "methodology_checklist": "methodology_checklist_bab_2_3.csv",
    "ms_params": "ms_garch_state_parameters.csv",
    "ms_transition": "ms_garch_transition_matrix.csv",
    "ms_filtered_prob": "ms_garch_filtered_probabilities_train.csv",
    "ms_smoothed_prob": "ms_garch_smoothed_probabilities_train.csv",
    "ms_state_vol": "ms_garch_state_volatility_train.csv",
    "sv_params": "sv_posterior_parameter_summary.csv",
    "sv_latent": "sv_latent_volatility_train.csv",
    "stationarity": "stationarity_tests.csv",
    "ljung_return": "ljung_box_return.csv",
    "ljung_squared": "ljung_box_squared_return.csv",
    "arch_lm": "arch_lm_test.csv",
    "distribution": "distribution_tail_summary.csv",
}

JSON_FILES = {
    "model_summary": "model_summary.json",
}

DATE_COLUMNS = ("open_time", "close_time", "forecast_date", "date", "timestamp")

DATE_COLUMN_BY_KEY = {
    "btc": "open_time",
    "btc_train": "open_time",
    "btc_test": "open_time",
    "risk": "open_time",
    "price_demo": "open_time",
    "ms_filtered_prob": "open_time",
    "ms_smoothed_prob": "open_time",
    "ms_state_vol": "open_time",
    "sv_latent": "open_time",
    "next_day": "forecast_date",
}
