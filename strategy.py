from events import SignalEvent
import numpy as np

class MovingAverageCrossStrategy:
    def __init__(self, data_handler, events_queue, short_window, long_window):
        self.data_handler = data_handler
        self.events_queue = events_queue
        self.short_window = short_window
        self.long_window = long_window
        self.ticker = self.data_handler.ticker
        
        self.bought = False # Simplified state: False means flat, True means long

    def calculate_signals(self, event):
        if event.type == 'MARKET':
            bars = self.data_handler.get_latest_bars(self.long_window + 1)
            
            if len(bars) >= self.long_window:
                # Calculate MAs
                closes = [b[1]['Close'] for b in bars]
                short_sma = np.mean(closes[-self.short_window:])
                long_sma = np.mean(closes[-self.long_window:])
                
                if len(closes) > self.long_window: # We have a previous interval
                    prev_short_sma = np.mean(closes[-self.short_window-1:-1])
                    prev_long_sma = np.mean(closes[-self.long_window-1:-1])
                else:
                    prev_short_sma = short_sma
                    prev_long_sma = long_sma

                date = self.data_handler.get_latest_bar_date()

                # Crossover logic
                if short_sma > long_sma and prev_short_sma <= prev_long_sma and not self.bought:
                    signal = SignalEvent(self.ticker, date, 'LONG')
                    self.events_queue.put(signal)
                    self.bought = True
                
                elif short_sma < long_sma and prev_short_sma >= prev_long_sma and self.bought:
                    signal = SignalEvent(self.ticker, date, 'EXIT')
                    self.events_queue.put(signal)
                    self.bought = False
