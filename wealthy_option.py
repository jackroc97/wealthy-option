from datetime import time, timedelta
from ib_async import *

from ibkrkit import *
    
def round_to_nearest_quarter(x: float) -> float:
    return round(x * 4) / 4


class WealthyOption(IbkrStrategy):
    name = "WealthyOptionStrategy"
    version = "0.1.0"
    log_db_path = "log.db"
    
    ES_contract = Future(symbol="ES", lastTradeDateOrContractMonth="202512", exchange="CME", currency="USD")
    time_min = time(9, 45)
    time_max = time(23, 45)
    dte_min = 1
    dte_max = 3
    desired_delta = -0.065
    spread_width = 50
    take_profit_pct = 0.7
    stop_loss_pct = 0.5
            

    async def on_start(self):
        self.print_msg("Strategy started.")
        await self.ib.qualifyContractsAsync(self.ES_contract)
        self.ES_data = await IbkrDataStream.create(self.ib, self.ES_contract)
        self.ES_options = await IbkrOptionChain.create(self.ib, self.ES_contract, max_strike_dist=200, max_dte=4, excluded_trading_classes=["ECES"])
        
        
    async def tick(self):
        self.print_msg(f"{self.ES_contract.symbol} spot price: ${self.ES_data.get('last'):.2f}")
        self.print_msg(f"Open orders: {self.trade_as_str(self.ib.openTrades())}")
        self.print_msg(f"Open positions: {self.position_as_str(self.ib.positions())}")
        
        if self.should_open_new_position():
            self.print_msg(f"Attempting to open a new position...")
            short_put = self.select_short_put()

            if short_put is not None:
                long_put = self.select_long_put(short_put)
                await self.ib.qualifyContractsAsync(short_put, long_put)
                                
                # Construct the spread order
                short_leg = ComboLeg(conId=short_put.conId, ratio=1, action="BUY", exchange=short_put.exchange)
                long_leg = ComboLeg(conId=long_put.conId, ratio=1, action="SELL", exchange=long_put.exchange)
                self.spread = Bag(symbol=self.ES_contract.symbol,
                                  exchange=self.ES_contract.exchange,
                                  currency=self.ES_contract.currency,
                                  comboLegs=[short_leg, long_leg])
                
                # Calculate the limit price, take profit, and stop loss
                sp_data = await IbkrDataStream.create(self.ib, short_put)
                lp_data = await IbkrDataStream.create(self.ib, long_put)
                limit_price = sp_data.get("bid") - lp_data.get("ask")
                take_profit_price = round_to_nearest_quarter((1 - self.take_profit_pct) * limit_price)
                stop_loss_price = round_to_nearest_quarter((1 + self.stop_loss_pct) * limit_price)

                # Place a bracket order for the spread
                trades = self.place_bracket_order(contract=self.spread, 
                                                 open_action="SELL",
                                                 quantity=1,
                                                 limit_price=limit_price,
                                                 take_profit_price=take_profit_price,
                                                 stop_loss_price=stop_loss_price)
                for trade in trades:
                    self.print_msg(f"Placed order: {self.trade_as_str(trade)}")
                    self.logger.log_order(trade.order, { "underlying_price": self.ES_data.get('last'), 
                                                         "short_put_delta": self.ES_options.get(short_put, "delta") })

    
    async def on_stop(self):
        self.print_msg(f"Strategy stopped.")
        
    
    def should_open_new_position(self) -> bool:
        in_session = self.now.time() >= self.time_min and \
            self.now.time() <= self.time_max      
        has_open_positions = len(self.ib.positions()) > 0
        has_open_orders = len(self.ib.openTrades()) > 0
        return in_session and not has_open_positions and not has_open_orders   
        
    
    def select_short_put(self) -> Contract | None:
        dte_min = self.dte_min
        dte_max = self.dte_max
        match self.now.weekday():
            case 4:
                dte_min = self.dte_min + 2
                dte_max = self.dte_max + 2
            
        for exp in [self.now + timedelta(days=d) for d in range(dte_min, dte_max)]:
            stk, delta = self.ES_options.find_best_strike_by_delta("P", exp.date(), self.desired_delta)
            if not None in (exp, stk, delta):
                self.print_msg(f"Selected short put: exp={exp.date()}, strike={stk}, delta={delta:.3f}")
                return FuturesOption(symbol=self.ES_contract.symbol, 
                                     lastTradeDateOrContractMonth=exp.strftime("%Y%m%d"), 
                                     strike=stk, 
                                     right='P', 
                                     exchange=self.ES_contract.exchange, 
                                     currency=self.ES_contract.currency)
        self.print_msg(f"Warning: Could not find a suitable expiration date!")
        return None 
        
        
    def select_long_put(self, short_put: Contract) -> Contract:
        return FuturesOption(symbol=short_put.symbol,
                             lastTradeDateOrContractMonth=short_put.lastTradeDateOrContractMonth, 
                             strike=short_put.strike - self.spread_width, 
                             right='P', 
                             exchange=short_put.exchange, 
                             currency=short_put.currency)
    
    
    def on_order_partial_fill(self, trade: Trade, fill: Fill):
        self.print_msg(f"##### ORDER FILL #####: {self.fill_as_str(fill)}")
        self.logger.log_fill(trade, fill)
