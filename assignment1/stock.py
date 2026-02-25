import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import seaborn as sb
import yfinance as yf  # Assuming yfinance for data API

sb.set_theme()

"""
STUDENT CHANGE LOG & AI DISCLOSURE:
----------------------------------
1. Did you use an LLM (ChatGPT/Claude/etc.)? [Yes/No]
2. If yes, what was your primary prompt?
----------------------------------
"""

DEFAULT_START = dt.date.isoformat(dt.date.today() - dt.timedelta(365))
DEFAULT_END = dt.date.isoformat(dt.date.today())


class Stock:
    def __init__(self, symbol, start=DEFAULT_START, end=DEFAULT_END):
        self.symbol = symbol
        self.start = start
        self.end = end
        self.data = self.get_data()

    def get_data(self):
        data = yf.download(self.symbol, start=self.start, end=self.end)
        data.index = pd.to_datetime(data.index)
        self.calc_returns(data)
        return data
    
        """Downloads data from yfinance and triggers return calculation."""
        # TODO: Use yf.download(self.symbol, start=self.start, end=self.end)
        # data = ...

        # self.calc_returns(data)
        # return data
        

    def calc_returns(self, df):
        df['Change'] = df['Close'].pct_change()
        df['Instant_Return'] = np.log(df['Close']).diff().round(4)
        """Adds 'Change', close to close and 'Instant_Return' columns to the dataframe."""
        # Requirement: Use vectorized pandas operations, not loops.
    
    def add_technical_indicators(self, windows=[20, 50]):
        for days in windows:
            columnname = f'SMA_{days}'
            self.data[columnname] = self.data['Close'].rolling(window=days).mean()
        self.data[['Close', 'SMA_20', 'SMA_50']].plot() 
        plt.legend()
        plt.show()
        """
        Add Simple Moving Averages (SMA) for the given windows
        to the internal DataFrame. Produce a plot showing the closing price and SMAs. 
        """

    def plot_return_dist(self):
        self.data['Instant_Return'].dropna().hist(bins=50)
        plt.xlabel("Date") 
        plt.ylabel("Price (USD)")
        plt.title(f"{self.symbol} Returns")
        plt.axvline(0, color='red')
        plt.show()

    def plot_performance(self):
        performance = (self.data['Close'] / self.data['Close'].iloc[0]) - 1
        plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        performance.plot() 
        plt.xlabel("Date") 
        plt.ylabel("Percentage Growth")
        plt.title(f"{self.symbol} Performance")
        plt.show()
        """Plots cumulative growth of $1 investment."""
        


def main():
    # Example usage:
    aapl = Stock("AAPL")
    aapl.plot_performance()
    aapl.add_technical_indicators()
    aapl.plot_return_dist()
    pass


if __name__ == "__main__":
    main()