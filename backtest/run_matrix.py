from datetime import datetime, time, timedelta

from btkit.utils.matrix_runner import MatrixRunner
from btkit.strategy import DateSettings

from wealthy_option import WealthyOption


MATRIX_PATH = "/Users/jrochester/dev/wealthy-option/backtest/doe/doe_2.yaml"
OUTPUT_PATH = "/Users/jrochester/dev/wealthy-option/backtest/logs/put_only_strategies.db"

date_settings = DateSettings(time(9, 35, 0), time(16, 0, 0), weekday_only=True)

matrix = MatrixRunner(WealthyOption, MATRIX_PATH)
matrix._resume_from(25, 10000, datetime(2025, 1, 2), datetime(2025, 10, 17), timedelta(minutes=5), OUTPUT_PATH, date_settings)
