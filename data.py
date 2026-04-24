import yfinance as yf
import pandas as pd
from events import MarketEvent

class DataHandler:
    def __init__(self, events_queue, ticker, start_date, end_date):
        self.events_queue = events_queue
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        
        self.symbol_data = None
        self.latest_symbol_data = [] # List of (date, dict_bar)
        self.continue_backtest = True
        
        self._download_data()
        if self.symbol_data is not None and not self.symbol_data.empty:
            self.generator = self._get_new_bar()
        else:
            self.generator = iter([])
            self.continue_backtest = False
        
    def _download_data(self):
        # Fetch the historical data
        ticker_obj = yf.Ticker(self.ticker)
        data = ticker_obj.history(start=self.start_date, end=self.end_date)
        if not data.empty:
            # We want timezone naive dates for simpler visual plotting
            if data.index.tz is not None:
                data.index = data.index.tz_convert(None)
            self.symbol_data = data.dropna()
            self.total_days = len(self.symbol_data)
        else:
            self.symbol_data = None
        
    def _get_new_bar(self):
        for date, row in self.symbol_data.iterrows():
            yield date, row

    def update_bars(self):
        """Pushes the next bar to the latest_symbol_data list and generates MarketEvent."""
        try:
            date, bar = next(self.generator)
            # Create a dictionary for the bar with date included
            bar_dict = {
                'Open': bar['Open'],
                'High': bar['High'],
                'Low': bar['Low'],
                'Close': bar['Close'],
                'Volume': bar['Volume']
            }
            self.latest_symbol_data.append((date, bar_dict))
            self.events_queue.put(MarketEvent())
        except StopIteration:
            self.continue_backtest = False

    def get_latest_bars(self, n=1):
        """Returns the last N bars."""
        return self.latest_symbol_data[-n:]

    def get_latest_bar_date(self):
        """Returns the date of the most recent bar."""
        if self.latest_symbol_data:
            return self.latest_symbol_data[-1][0]
        return None
