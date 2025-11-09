from datetime import date, datetime, timedelta, time
from btkit.strategy import DateSettings
from wealthy_option import WealthyOption


if __name__ == "__main__":
    date_settings = DateSettings(time(9, 35, 0), time(16, 0, 0), weekday_only=True, skip_dates=[date(2023, 12, 25)])
    strat = WealthyOption(10000, datetime(2025, 7, 18), datetime(2025, 10, 17), timedelta(minutes=5), "/Users/jrochester/dev/wealthy-option/backtest/logs/log.db", date_settings)
    strat.run()
    