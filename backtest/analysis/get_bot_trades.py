import pandas as pd
from datetime import date, datetime, timedelta
from ib_async import *

# Expires 10/10/2026
TOKEN = 764715579278357432895699
QUERY_ID = 1307213
 
COLUMNS = ["dateTime", "fifoPnlRealized", "tradeID", "openCloseIndicator", "tradePrice", "buySell", "quantity", "symbol", "conid", "expiry", "strike", "putCall", "closePrice"]

def get_trades(start_date: datetime = None, end_date: datetime = None):
    # Get all trades from flex report
    trades_report = FlexReport(TOKEN, QUERY_ID)
    df = trades_report.df("Trade")
    
    # Filter by date
    df["dateTime"] = pd.to_datetime(df["dateTime"], format="%Y%m%d;%H%M%S")
    mask = pd.Series(True, index=df.index)
    if start_date is not None:
        mask &= df["dateTime"] >= start_date
    if end_date is not None:
        mask &= df["dateTime"] <= end_date
    df = df[mask]
    df = df.sort_values("dateTime", ascending=True).reset_index(drop=True)
    return df


def print_daily_report(date: datetime):
    trades = get_trades(start_date=date, end_date=date+timedelta(days=1))
    print("### Trades ###")
    for _, row in trades.iterrows():
        action = row['buySell'][0] + "T" + row['openCloseIndicator']
        print(f"{row['dateTime']} {action} {row['quantity']: >2}x{row['multiplier']} {row['underlyingSymbol']} {row['expiry']} {row['strike']} {row['putCall']} @ ${row['tradePrice']:.2f} (${row['fifoPnlRealized']:.2f})")
    
    # mtmPnl does not include commissions, whereas fifo does
    daily_pnl = trades['fifoPnlRealized'].sum()
    print("### PnL ###")
    print(f"${daily_pnl:.2f}")
 
if __name__ == "__main__":
    print_daily_report(datetime(2025, 10, 15))
    #print(get_trades(datetime(2025, 10, 13))[["dateTime", "symbol", "expiry"]])