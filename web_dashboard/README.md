# BitRisk

Thesis dashboard for **Bitcoin Volatility and Risk Modeling via Markov-Switching GARCH and Stochastic Volatility: VaR and CVaR Analysis**.

The statistical workflow is prepared in `Stat_Final_Code.ipynb`. BitRisk presents the exported CSV/JSON outputs as an interactive dashboard for review and reporting.

## Project Structure

```text
web_dashboard/
    app.py
    requirements.txt
    README.md
    .streamlit/
        config.toml
    src/
        __init__.py
        constants.py
        data_loader.py
        formatting.py
        charts.py
        components.py
```

## Expected Workflow

1. Run `Stat_Final_Code.ipynb` first.
2. Make sure the notebook exports CSV/JSON files to `outputs/` at the project root.
3. Run the Streamlit dashboard.

In this workspace, the available exported files are currently in `outputs_optimized_notebook/`.

## Run

From the project root:

```bash
pip install -r web_dashboard/requirements.txt
streamlit run web_dashboard/app.py
```

From inside the dashboard folder:

```bash
cd web_dashboard
pip install -r requirements.txt
streamlit run app.py
```

## Expected Output Files

The dashboard reads files such as:

```text
outputs/btc_preprocessed_optimized.csv
outputs/btc_train_optimized.csv
outputs/btc_test_optimized.csv
outputs/oos_risk_forecasts.csv
outputs/price_forecast_demo.csv
outputs/backtesting_summary.csv
outputs/model_comparison_rank.csv
outputs/best_model_by_confidence.csv
outputs/next_day_risk_forecast.csv
outputs/ms_garch_state_parameters.csv
outputs/ms_garch_transition_matrix.csv
outputs/ms_garch_filtered_probabilities_train.csv
outputs/ms_garch_smoothed_probabilities_train.csv
outputs/ms_garch_state_volatility_train.csv
outputs/sv_posterior_parameter_summary.csv
outputs/sv_latent_volatility_train.csv
outputs/stationarity_tests.csv
outputs/ljung_box_return.csv
outputs/ljung_box_squared_return.csv
outputs/arch_lm_test.csv
outputs/distribution_tail_summary.csv
outputs/model_summary.json
```

Missing files are reported in the UI without substituting unavailable model results.

## Pages

- Dashboard: daily BTC risk overview, KPI cards, price/return/volatility charts, VaR breach view, and daily risk table.
- Models & Diagnostics: methodology overview, model comparison, MS-GARCH outputs, SV outputs, and diagnostics.
- Backtesting: VaR breach metrics, Kupiec and Christoffersen test outputs, breach events, and MS-GARCH vs SV comparison.
- Forecast: next-day VaR/CVaR cards and one-step-ahead price forecast chart.
- About: thesis metadata, methodology scope, sample coverage, and empirical workflow.
