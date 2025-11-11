"""
Data Collection Module
Handles fetching stock data from Finnhub and Yahoo Finance APIs
"""

import finnhub
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from pathlib import Path
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCollector:
    """Collects stock market data from multiple sources"""

    def __init__(self, api_key: str, data_dir: Path):
        """
        Initialize data collector

        Args:
            api_key: Finnhub API key
            data_dir: Directory to store collected data
        """
        self.finnhub_client = finnhub.Client(api_key=api_key) if api_key else None
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)

    def get_stock_quote(self, symbol: str) -> Optional[Dict]:
        """
        Get current quote for a stock

        Args:
            symbol: Stock symbol (e.g., 'ENI.MI')

        Returns:
            Dictionary with quote data or None if error
        """
        if not self.finnhub_client:
            logger.warning("Finnhub client not initialized. Using Yahoo Finance fallback.")
            return self._get_yahoo_quote(symbol)

        try:
            # Convert symbol format for Finnhub
            finnhub_symbol = symbol.replace('.MI', ':MI')
            quote = self.finnhub_client.quote(finnhub_symbol)

            if quote and quote.get('c', 0) > 0:
                return {
                    'symbol': symbol,
                    'current_price': quote['c'],
                    'change': quote['d'],
                    'percent_change': quote['dp'],
                    'high': quote['h'],
                    'low': quote['l'],
                    'open': quote['o'],
                    'previous_close': quote['pc'],
                    'timestamp': datetime.now()
                }
            else:
                # Finnhub didn't return valid data, fallback to Yahoo Finance
                logger.warning(f"Finnhub returned invalid data for {symbol}, using Yahoo Finance fallback")
                return self._get_yahoo_quote(symbol)
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol} from Finnhub: {e}")
            return self._get_yahoo_quote(symbol)

    def _get_yahoo_quote(self, symbol: str) -> Optional[Dict]:
        """Fallback to Yahoo Finance for quote data"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period='2d')

            if not hist.empty:
                latest = hist.iloc[-1]
                previous = hist.iloc[-2] if len(hist) > 1 else hist.iloc[-1]

                return {
                    'symbol': symbol,
                    'current_price': latest['Close'],
                    'change': latest['Close'] - previous['Close'],
                    'percent_change': ((latest['Close'] - previous['Close']) / previous['Close']) * 100,
                    'high': latest['High'],
                    'low': latest['Low'],
                    'open': latest['Open'],
                    'previous_close': previous['Close'],
                    'timestamp': datetime.now()
                }
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol} from Yahoo: {e}")

        return None

    def get_historical_data(self, symbol: str, days: int = 730) -> pd.DataFrame:
        """
        Get historical stock data

        Args:
            symbol: Stock symbol
            days: Number of days of historical data

        Returns:
            DataFrame with historical data
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Use Yahoo Finance for historical data (more reliable for Italian stocks)
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)

            if df.empty:
                logger.warning(f"No historical data found for {symbol}")
                return pd.DataFrame()

            # Standardize column names
            df = df.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })

            # Add symbol column
            df['symbol'] = symbol

            # Save to CSV
            csv_path = self.data_dir / f"{symbol.replace('.', '_')}_historical.csv"
            df.to_csv(csv_path)
            logger.info(f"Saved historical data for {symbol} to {csv_path}")

            return df

        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()

    def get_company_news(self, symbol: str, days: int = 7) -> List[Dict]:
        """
        Get company news from Finnhub

        Args:
            symbol: Stock symbol
            days: Number of days of news to fetch

        Returns:
            List of news articles
        """
        if not self.finnhub_client:
            logger.warning("Finnhub client not initialized. Cannot fetch news.")
            return []

        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            finnhub_symbol = symbol.replace('.MI', ':MI')
            news = self.finnhub_client.company_news(
                finnhub_symbol,
                _from=start_date.strftime('%Y-%m-%d'),
                to=end_date.strftime('%Y-%m-%d')
            )

            return news if news else []

        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return []

    def get_institutional_ownership(self, symbol: str) -> Optional[Dict]:
        """
        Get institutional ownership data

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with ownership data or None
        """
        if not self.finnhub_client:
            return None

        try:
            finnhub_symbol = symbol.replace('.MI', ':MI')
            ownership = self.finnhub_client.institutional_ownership(finnhub_symbol)
            return ownership
        except Exception as e:
            logger.error(f"Error fetching institutional ownership for {symbol}: {e}")
            return None

    def collect_all_data(self, symbols: List[str], historical_days: int = 730) -> Dict:
        """
        Collect all data for multiple symbols

        Args:
            symbols: List of stock symbols
            historical_days: Days of historical data

        Returns:
            Dictionary with all collected data
        """
        all_data = {
            'quotes': {},
            'historical': {},
            'news': {},
            'ownership': {}
        }

        for symbol in symbols:
            logger.info(f"Collecting data for {symbol}...")

            # Current quote
            quote = self.get_stock_quote(symbol)
            if quote:
                all_data['quotes'][symbol] = quote

            # Historical data
            hist = self.get_historical_data(symbol, historical_days)
            if not hist.empty:
                all_data['historical'][symbol] = hist

            # News
            news = self.get_company_news(symbol)
            all_data['news'][symbol] = news

            # Institutional ownership
            ownership = self.get_institutional_ownership(symbol)
            if ownership:
                all_data['ownership'][symbol] = ownership

            # Respect API rate limits
            time.sleep(1)

        logger.info(f"Data collection completed for {len(symbols)} symbols")
        return all_data


if __name__ == "__main__":
    # Test the data collector
    from config.config import FINNHUB_API_KEY, DATA_DIR, TOP_ITALIAN_STOCKS

    collector = DataCollector(FINNHUB_API_KEY, DATA_DIR)

    # Test with one stock
    test_symbol = TOP_ITALIAN_STOCKS[0]
    print(f"\nTesting with {test_symbol}:")

    quote = collector.get_stock_quote(test_symbol)
    print(f"Quote: {quote}")

    hist = collector.get_historical_data(test_symbol, days=30)
    print(f"Historical data shape: {hist.shape}")
