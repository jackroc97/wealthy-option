from datetime import timedelta, time

from btkit.instrument import InstrumentStore, OptionRight, Option
from btkit.order import Order, OrderAction
from btkit.strategy import Strategy


class WealthyOption(Strategy):
    name = "TestStrat"
    version = "0.1.0"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set strategy params
        self.design_id = kwargs.get("design_id", 0)
        self.strategy_type = kwargs.get("strategy_type", "short_put_spread")
        self.call_delta = kwargs.get("call_delta", 0.03)
        self.call_spread_width = kwargs.get("call_spread_width", 50)
        self.put_delta = kwargs.get("put_delta", -0.065)
        self.put_spread_width = kwargs.get("put_spread_width", 50)
        self.dte = kwargs.get("dte", 1)
        self.take_profit_pct = kwargs.get("take_profit_pct", 0.7)
        self.time_min = time(9, 45)
        self.time_max = time(14, 30)
        
        # Connect to the instrument database for this strategy
        InstrumentStore.connect_database("/Users/jrochester/dev/data/es_futures.duckdb")
        
        
    def on_start(self):
        self.ES = InstrumentStore.spot_future("ES")
            
    
    def tick(self):
        if self.should_open_new_position():
            self.open_position()
        else:
            self.try_take_profit()
            
    
    def on_stop(self):
        InstrumentStore.disconnect_database()
        
        
    def should_open_new_position(self) -> bool:
        in_session = self.now.time() >= self.time_min and \
            self.now.time() <= self.time_max      
        has_open_positions = len(self.broker.positions) > 0
        return in_session and not has_open_positions
        
        
    def open_position(self):
        orders: list[Order] = []
        
        # Every strategy type uses a short put, so find that first
        short_put = self.select_short_option(OptionRight.PUT, self.put_delta)
        if short_put is None:
            return
        
        orders.append(Order(OrderAction.STO, 1, short_put))
            
        if self.strategy_type == "short_strangle":
            short_call = self.select_short_option(OptionRight.CALL, self.call_delta)
            orders.append(Order(OrderAction.STO, 1, short_call))
            
        elif self.strategy_type == "short_put_spread":
            long_put = self.select_long_option(short_put, -self.put_spread_width)
            orders.append(Order(OrderAction.BTO, 1, long_put))
            
        elif self.strategy_type == "short_iron_condor":
            short_call = self.select_short_option(OptionRight.CALL, self.call_delta)
            if short_call is None:
                return
            
            orders.append(Order(OrderAction.STO, 1, short_call))
            
            long_put = self.select_long_option(short_put, -self.put_spread_width)
            orders.append(Order(OrderAction.BTO, 1, long_put))
            
            long_call = self.select_long_option(short_call, self.call_spread_width)
            orders.append(Order(OrderAction.BTO, 1, long_call))
        
        # Do nothing if we can't construct the option strategy correctly
        if any([(ord.instrument is None) for ord in orders]):
            return
        
        self.broker.open_position(*orders)
        
        
    def select_short_option(self, option_right: OptionRight, delta: float):
        dte_min = self.dte
        dte_max = self.dte + 3
        
        # Map datetime -> dte
        for exp, dte in {(self.now + timedelta(days=d)): d for d in range(dte_min, dte_max)}.items():
            if (exp.weekday() >= 5):  # skip weekends
                continue
            
            matches = self.ES.at(self.now).search_options_by_delta(delta, dte, option_right)
            if len(matches):
                return InstrumentStore.instrument_by_id(matches.iloc[0]['instrument_id'], Option)
                
        # Did not find a suitable option
        return None 
    
    
    def select_long_option(self, short_option: Option, strike_shift: float):
        return InstrumentStore.option(self.ES.at(self.now), short_option.expiration.date(), short_option.strike_price + strike_shift, short_option.right)
    
    
    def try_take_profit(self) -> bool:
        for position in self.broker.positions:
            if position.pnl_pct > self.take_profit_pct:
                self.broker.close_position(position)
    