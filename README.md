# Event-Driven Trading Backtester

A modular, event-driven algorithmic trading backtester built in Python. This system utilizes a centralized event queue to process market data, strategy signals, and portfolio orders. It includes a Moving Average Crossover strategy as a core implementation example.

The project features an interactive **Streamlit** dashboard that allows users to adjust strategy parameters on the fly, visualize trading performance using Plotly charts, and track key financial metrics.

## Features
- **Event-Driven Architecture**: Processes market data, signals, and execution orders through a centralized event queue.
- **Moving Average Crossover Strategy**: A built-in example strategy to demonstrate signal generation.
- **Interactive Dashboard**: A frontend built with Streamlit to configure parameters and visualize results.
- **Performance Tracking**: Calculates and displays key metrics and portfolio equity curves.

## How to Run

1. **Install Dependencies**
   It's recommended to use a virtual environment. Install the required Python packages by running:
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch the Streamlit Dashboard**
   You can start the visual interface by running the following command in your terminal:
   ```bash
   streamlit run app.py
   ```
   This will start a local web server and automatically open the application in your default web browser (usually at `http://localhost:8501`).