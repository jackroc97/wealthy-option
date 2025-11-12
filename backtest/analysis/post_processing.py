import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

from datetime import datetime

from btkit.utils.post_processing import PostprocTool

tool = PostprocTool("/Users/jrochester/dev/wealthy-option/backtest/logs/put_only_strategies.db")

print(tool.session_df[["id", "net_profit", "percent_profitable", "max_drawdown", "cagr", "sharpe_ratio"]].sort_values("net_profit", ascending=False))

tool.summarize(58)

fig = tool.equity_curve(58, show=False)

spy = yf.download("SPY", period="1y", interval="1d")
spy["time"] = pd.to_datetime(spy.index, format="%Y-%m-%d")
spy['investment_value'] = 10000 * (spy['Close'] / spy['Close'].iloc[0])
spy = spy[spy["time"] > datetime(2025, 1, 2)]
fig.add_trace(go.Scatter(x=spy["time"], y=spy["investment_value"].to_numpy().flatten(), name="SPY"))
fig.show()

tool.pnl_histogram(58)
tool.trade_scatterplot(58)
tool.heatmap("net_profit", {'strategy_type': 'short_put_spread', 'dte': 1}, "take_profit_pct", "put_delta")
