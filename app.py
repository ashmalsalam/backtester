import streamlit as st
import queue
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from data import DataHandler
from strategy import MovingAverageCrossStrategy
from portfolio import PortfolioManager
from engine import BacktestEngine
from plotly.subplots import make_subplots

st.set_page_config(page_title="Algorithmic Trading Backtester", layout="wide")

st.title("Event-Driven Algorithmic Trading Backtester")
st.markdown("A complete, modular backtesting engine simulating live market behavior using an event-driven architecture.")

st.sidebar.header("Strategy Parameters")
ticker = st.sidebar.text_input("Ticker Symbol", value="AAPL")
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2023-01-01"))

short_window = st.sidebar.slider("Fast/Short MA Window", 5, 50, 20)
long_window = st.sidebar.slider("Slow/Long MA Window", 20, 200, 50)
initial_capital = st.sidebar.number_input("Initial Capital ($)", value=10000)

if st.sidebar.button("Run Backtest"):
    with st.spinner("Running Event-Driven Backtest..."):
        # Setup Event Queue
        events_queue = queue.Queue()
        
        # Initialize modules
        data_handler = DataHandler(events_queue, ticker, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        
        if data_handler.symbol_data is None or data_handler.symbol_data.empty:
            st.error(f"No data found for {ticker} between {start_date} and {end_date}.")
            st.stop()
            
        strategy = MovingAverageCrossStrategy(data_handler, events_queue, short_window, long_window)
        portfolio = PortfolioManager(data_handler, events_queue, initial_capital)
        
        # Engine
        engine = BacktestEngine(data_handler, strategy, portfolio)
        
        # Run
        equity_curve, trades_df = engine.run()
        
        if equity_curve is None or equity_curve.empty:
            st.error("No equity curve generated. Possibly not enough data or errors in loop.")
            st.stop()
            
        # Compute MAs for plotting 
        price_data = data_handler.symbol_data.copy()
        price_data['Fast_MA'] = price_data['Close'].rolling(window=short_window).mean()
        price_data['Slow_MA'] = price_data['Close'].rolling(window=long_window).mean()
        
        # Compute Metrics
        final_capital = equity_curve['Total'].iloc[-1]
        total_return = ((final_capital - initial_capital) / initial_capital) * 100
        num_trades = len(trades_df) if not trades_df.empty else 0
        
        # Metrics Display
        col1, col2, col3 = st.columns(3)
        col1.metric("Final Capital", f"${final_capital:,.2f}", f"{final_capital - initial_capital:,.2f}")
        col2.metric("Total Return", f"{total_return:.2f}%")
        col3.metric("Total Trades", num_trades)
        
        # Plot Charts
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.05, 
                            row_heights=[0.7, 0.3])
                            
        # Price and MAs
        fig.add_trace(go.Scatter(x=price_data.index, y=price_data['Close'], mode='lines', name='Price', line=dict(color='gray', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=price_data.index, y=price_data['Fast_MA'], mode='lines', name=f'Fast MA ({short_window})', line=dict(color='blue', width=1.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=price_data.index, y=price_data['Slow_MA'], mode='lines', name=f'Slow MA ({long_window})', line=dict(color='orange', width=1.5)), row=1, col=1)
        
        # Buy/Sell Markers
        if not trades_df.empty:
            buy_trades = trades_df[trades_df['Action'] == 'BUY']
            sell_trades = trades_df[trades_df['Action'] == 'SELL']
            
            if not buy_trades.empty:
                fig.add_trace(go.Scatter(x=buy_trades['Date'], y=buy_trades['Price'], mode='markers', name='Buy',
                                         marker=dict(symbol='triangle-up', size=12, color='green')), row=1, col=1)
            if not sell_trades.empty:
                fig.add_trace(go.Scatter(x=sell_trades['Date'], y=sell_trades['Price'], mode='markers', name='Sell',
                                         marker=dict(symbol='triangle-down', size=12, color='red')), row=1, col=1)

        # Equity Curve
        fig.add_trace(go.Scatter(x=equity_curve.index, y=equity_curve['Total'], mode='lines', name='Equity', line=dict(color='green', width=2)), row=2, col=1)
        
        fig.update_layout(height=800, title_text="Backtest Results", showlegend=True, hovermode='x unified')
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Price / Value", row=1, col=1)
        fig.update_yaxes(title_text="Portfolio Total ($)", row=2, col=1)
        
        st.plotly_chart(fig, width='stretch')
        
        if not trades_df.empty:
            st.subheader("Trade Log")
            st.dataframe(trades_df.style.format({'Price': '${:.2f}', 'Commission': '${:.2f}'}), width='stretch')
