import queue

class BacktestEngine:
    def __init__(self, data_handler, strategy, portfolio):
        self.events_queue = data_handler.events_queue
        self.data_handler = data_handler
        self.strategy = strategy
        self.portfolio = portfolio
        
    def run(self):
        while True:
            # Update the market bars
            if self.data_handler.continue_backtest:
                self.data_handler.update_bars()
            else:
                break
                
            # Process ALL generated events for this timestep
            while True:
                try:
                    event = self.events_queue.get(False)
                except queue.Empty:
                    break
                    
                if event is not None:
                    if event.type == 'MARKET':
                        self.strategy.calculate_signals(event)
                        self.portfolio.update_timeindex(event)
                    elif event.type == 'SIGNAL':
                        self.portfolio.update_signal(event)
                    elif event.type == 'ORDER':
                        self.portfolio.simulate_execution(event)
                    elif event.type == 'FILL':
                        self.portfolio.update_fill(event)

        # Output basic stats
        eq = self.portfolio.get_equity_curve_df()
        trades = self.portfolio.get_trades_df()
        return eq, trades
