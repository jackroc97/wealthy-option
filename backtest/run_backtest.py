from datetime import date, datetime, timedelta, time
from btkit.strategy import DateSettings
from wealthy_option import WealthyOption

# >> What happens on 08-26-25 ? symbols and strikes dont match?
# cant reproduce it if starting on 8/26/25... only if starting from 7/18
# >> ValueError: No option found for underlying ID 294973 on 2025-10-02
if __name__ == "__main__":
    date_settings = DateSettings(time(9, 35, 0), time(16, 0, 0), weekday_only=True, skip_dates=[date(2023, 12, 25)])
    strat = WealthyOption(10000, datetime(2025, 7, 17), datetime(2025, 10, 18, 0, 0, 0), timedelta(minutes=5), "./logs/log.db", date_settings)
    strat.run()
    