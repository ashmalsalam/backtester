import pandas as pd
from events import OrderEvent, FillEvent

class PortfolioManager:
    def __init__(self, data_handler, events_queue, initial_capital=10000.0):
        self.data_handler = data_handler
        self.events_queue = events_queue
        self.initial_capital = initial_capital
        
        self.current_cash = initial_capital
        self.current_positions = {self.data_handler.ticker: 0}
        self.current_holdings = {self.data_handler.ticker: 0.0}
        
        self.equity_curve = [] # List of dicts to form a DataFrame later
        self.trades = [] # Keep track of fills

    def update_timeindex(self, event):
        """Triggered on MARKET event. Appends the current equity."""
        latest_bars = self.data_handler.get_latest_bars(1)
        if not latest_bars:
            return
            
        date, bar = latest_bars[0]
        ticker = self.data_handler.ticker
        
        price = bar['Close']
        position = self.current_positions[ticker]
        
        # update holdings value
        holding_value = position * price
        
        total_equity = self.current_cash + holding_value
        
        self.equity_curve.append({
            'Date': date,
            'Cash': self.current_cash,
            'Holdings': holding_value,
            'Total': total_equity
        })

    def update_signal(self, event):
        """Triggered on SIGNAL event. Generates ORDER events."""
        if event.type == 'SIGNAL':
            ticker = event.ticker
            date = event.date
            
            # Simple fixed sizing: buy all we can on LONG, sell all on EXIT
            if event.signal_type == 'LONG':
                latest_bars = self.data_handler.get_latest_bars(1)
                price = latest_bars[0][1]['Close']
                
                # Buy all we can
                quantity = int(self.current_cash // price)
                if quantity > 0:
                    order = OrderEvent(ticker, date, 'MKT', quantity, 'BUY')
                    self.events_queue.put(order)
                    
            elif event.signal_type == 'EXIT':
                quantity = self.current_positions[ticker]
                if quantity > 0:
                    order = OrderEvent(ticker, date, 'MKT', quantity, 'SELL')
                    self.events_queue.put(order)

    def simulate_execution(self, event):
        """Triggered on ORDER event. Simulates immediate fill at current close price."""
        if event.type == 'ORDER':
            latest_bars = self.data_handler.get_latest_bars(1)
            price = latest_bars[0][1]['Close']
            date = latest_bars[0][0]
            
            fill_event = FillEvent(
                timeindex=date,
                ticker=event.ticker,
                exchange='SIM',
                quantity=event.quantity,
                direction=event.direction,
                fill_cost=price
            )
            self.events_queue.put(fill_event)

    def update_fill(self, event):
        """Triggered on FILL event. Updates cash and positions."""
        if event.type == 'FILL':
            fill_dir = 1 if event.direction == 'BUY' else -1
            fill_cost = event.fill_cost
            quantity = event.quantity
            
            cost = fill_dir * fill_cost * quantity
            
            # Update cash and positions
            self.current_cash -= cost - event.commission
            self.current_positions[event.ticker] += fill_dir * quantity
            
            self.trades.append({
                'Date': event.timeindex,
                'Ticker': event.ticker,
                'Action': event.direction,
                'Quantity': quantity,
                'Price': fill_cost,
                'Commission': event.commission
            })

    def get_equity_curve_df(self):
        df = pd.DataFrame(self.equity_curve)
        if not df.empty:
            df.set_index('Date', inplace=True)
            # Recompute total as cash + holdings just in case (we did it row by row, this is fine)
        return df

    def get_trades_df(self):
        df = pd.DataFrame(self.trades)
        return df
