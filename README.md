# wealthy-option
This repo contains backtests and live implementations of the [WealthyOption](https://wealthyoption.com/) trading strategy.

## Running Backtest

1. In `wealthy-option`, change directory to the `backtest` directory
2. Run `run_backtest.py`

## Running Live (Paper or "Real" Trading)

### Run locally

1. Start IB Gateway program
2. In `wealthy-option`, change directory to the `live` directory
3. Ensure the correct python venv is activated.
4. Run `source setup-dev.sh` 
5. Run `./app/main.py`

### Run containerized app using docker-compose

1. Ensure any changes to requirements have been pushed to their main brach in git
2. In `wealthy-option`, change directory to the `live` directory
3. `docker-compose up`

In either case, logs are written to `wealthy-option/live/logs` directory.
