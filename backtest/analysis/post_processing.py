from btkit.postproc_tool import PostprocTool

tool = PostprocTool("/Users/jrochester/dev/wealthy-option/backtest/logs/log.db", 16, 10000)

tool.strategy_metrics()
tool.equity_curve()
tool.pnl_histogram()
tool.pnl_scatterplot()
