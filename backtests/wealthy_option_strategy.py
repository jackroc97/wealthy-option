from datetime import date, datetime, timedelta, time

from btkit.instrument import Instrument, InstrumentStore, OptionRight, Option
from btkit.order import Order
from btkit.strategy import Strategy, DateSettings


class TestStrat(Strategy):
    name = "TestStrat"
    version = "0.1.0"
    
    time_min = time(9, 45)
    time_max = time(23, 45)
    dte_min = 0
    dte_max = 3
    desired_delta = -0.065
    spread_width = 50
    take_profit_pct = 0.7
    stop_loss_pct = 0.5
    
    
    def on_start(self):
        self.print_msg("Starting!")
        InstrumentStore.connect_database("/Users/jrochester/dev/data/es_futures.duckdb")
        self.ES = InstrumentStore.spot_future("ES")
            
    
    def tick(self):
        self.print_msg(f"ES close price: {self.ES.at(self.now).get('close')}")
         
        if self.should_open_new_position():
            short_put = self.select_short_put()
            if short_put is not None:
                long_put = self.select_long_put(short_put)
                self.broker.open_position(Order(-1, short_put), Order(1, long_put))
    
        else:
            self.print_msg(",".join(str(p) + f" PnL = ${p.pnl:.2f}, MKT = ${p.market_price:.2f}" for p in self.broker.positions))
    
         
    def on_stop(self):
        self.print_msg("Stopped!")
        self.print_msg(self.broker.cash_balance)
        
        
    def should_open_new_position(self) -> bool:
        in_session = self.now.time() >= self.time_min and \
            self.now.time() <= self.time_max      
        has_open_positions = len(self.broker.positions) > 0
        #has_open_orders = len(self.broker.orders) > 0
        return in_session and not has_open_positions #and not has_open_orders   
        
        
    def select_short_put(self):
        dte_min = self.dte_min
        dte_max = self.dte_max
        if self.now.weekday() >= 4:
            dte_max = self.dte_max + 2
        
        # Map datetime -> dte
        for exp, dte in {(self.now + timedelta(days=d)): d for d in range(dte_min, dte_max)}.items():
            if (exp.weekday() >= 5):  # skip weekends
                continue
            
            matches = self.ES.at(self.now).search_options_by_delta(self.desired_delta, dte, OptionRight.PUT)
            if len(matches):
                match = matches.iloc[0]
                self.print_msg(f"Selected short put: exp={exp.date()}, strike={match['strike_price']}, delta={match['delta']:.3f}")
                return InstrumentStore.instrument_by_id(match['instrument_id'], Option)

        self.print_msg(f"Warning: Could not find a suitable expiration date!")
        return None 
    
    
    def select_long_put(self, short_put: Option) -> Instrument:
        return InstrumentStore.option(self.ES.at(self.now), short_put.expiration.date(), short_put.strike_price - self.spread_width, OptionRight.PUT)

    
# >> What happens on 08-26-25 ? symbols and strikes dont match?
# cant reproduce it if starting on 8/26/25... only if starting from 7/18
# >> ValueError: No option found for underlying ID 294973 on 2025-10-02
if __name__ == "__main__":
    date_settings = DateSettings(time(9, 35, 0), time(16, 0, 0), weekday_only=True, skip_dates=[date(2023, 12, 25)])
    strat = TestStrat(10000, datetime(2025, 7, 17), datetime(2025, 10, 18, 0, 0, 0), timedelta(minutes=5), "log.db", date_settings)
    strat.run()
    