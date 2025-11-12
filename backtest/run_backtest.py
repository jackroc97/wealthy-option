from datetime import date, datetime, timedelta, time
from btkit.strategy import DateSettings
from wealthy_option import WealthyOption


if __name__ == "__main__":
    date_settings = DateSettings(time(9, 30, 0), time(16, 0, 0), weekday_only=True, skip_dates=[date(2023, 12, 25)])
    
    run_settings = {"design_id": 25, "dte": 0, "put_delta": -0.065, "put_spread_widths": None, "strategy_type": "short_put", "take_profit_pct": 0.5}
    strat = WealthyOption(**run_settings)
    strat.run_backtest(10000, datetime(2025, 7, 3), datetime(2025, 10, 17), timedelta(minutes=5), "/Users/jrochester/dev/wealthy-option/backtest/logs/log_3.db", date_settings)
    