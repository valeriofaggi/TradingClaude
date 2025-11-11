"""
Lightweight Data Collector for GitHub Actions
Collects stock data using only Yahoo Finance (no API keys needed)
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import logging
import json
import sys
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Default stock symbols (Italian stocks)
DEFAULT_STOCKS = [
    "ENI.MI",
    "ISP.MI",
    "UCG.MI",
    "ENEL.MI",
    "A2A.MI",
    "TIT.MI",
    "G.MI",
    "RACE.MI",
    "BAMI.MI",
    "TEN.MI",
]


def is_market_hours():
    """
    Check if current time is within market hours (9:00-18:00 Mon-Fri)
    Note: GitHub Actions runs on UTC, Italian market is UTC+1/UTC+2
    """
    now = datetime.now()

    # Check if weekday (0=Monday, 4=Friday)
    if now.weekday() > 4:
        logger.info("Weekend - market closed")
        return False

    # Check if within reasonable hours (relaxed check for different timezones)
    hour = now.hour
    if hour < 6 or hour > 20:  # Outside 6AM-8PM UTC (covers market hours)
        logger.info(f"Outside market hours (UTC hour: {hour})")
        return False

    return True


def get_stock_list():
    """Get stock list from custom_stocks.json or use defaults"""
    custom_file = DATA_DIR / "custom_stocks.json"

    if custom_file.exists():
        try:
            with open(custom_file, 'r') as f:
                data = json.load(f)
                stocks = data.get('stocks', DEFAULT_STOCKS)
                logger.info(f"Loaded {len(stocks)} stocks from custom_stocks.json")
                return stocks
        except Exception as e:
            logger.warning(f"Error loading custom stocks: {e}, using defaults")

    return DEFAULT_STOCKS


def get_current_quote(symbol):
    """
    Get current quote for a stock symbol

    Args:
        symbol: Stock symbol (e.g., 'ENI.MI')

    Returns:
        Dictionary with quote data or None if error
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='2d')

        if hist.empty or len(hist) < 1:
            logger.warning(f"No data available for {symbol}")
            return None

        latest = hist.iloc[-1]
        previous = hist.iloc[-2] if len(hist) > 1 else hist.iloc[-1]

        quote = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'current_price': float(latest['Close']),
            'open': float(latest['Open']),
            'high': float(latest['High']),
            'low': float(latest['Low']),
            'volume': int(latest['Volume']),
            'previous_close': float(previous['Close']),
            'change': float(latest['Close'] - previous['Close']),
            'percent_change': float(((latest['Close'] - previous['Close']) / previous['Close']) * 100)
        }

        logger.info(f"✓ {symbol}: €{quote['current_price']:.2f} ({quote['percent_change']:+.2f}%)")
        return quote

    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {e}")
        return None


def update_historical_data(symbol, days=730):
    """
    Update historical data for a stock symbol

    Args:
        symbol: Stock symbol
        days: Number of days of historical data to fetch

    Returns:
        True if successful, False otherwise
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)

        if df.empty:
            logger.warning(f"No historical data for {symbol}")
            return False

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
        csv_filename = f"{symbol.replace('.', '_')}_historical.csv"
        csv_path = DATA_DIR / csv_filename
        df.to_csv(csv_path)

        logger.info(f"✓ Updated historical data for {symbol} ({len(df)} records)")
        return True

    except Exception as e:
        logger.error(f"Error updating historical data for {symbol}: {e}")
        return False


def update_predictions_history(quote):
    """
    Append current quote to predictions history CSV

    Args:
        quote: Dictionary with quote data
    """
    try:
        history_file = DATA_DIR / "predictions_history.csv"

        # Create DataFrame from quote
        df_new = pd.DataFrame([{
            'timestamp': quote['timestamp'],
            'symbol': quote['symbol'],
            'actual_price': quote['current_price'],
        }])

        # Append or create file
        if history_file.exists():
            df_existing = pd.read_csv(history_file)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined.to_csv(history_file, index=False)
        else:
            df_new.to_csv(history_file, index=False)

        logger.debug(f"Updated predictions history for {quote['symbol']}")

    except Exception as e:
        logger.error(f"Error updating predictions history: {e}")


def save_collection_log(stats):
    """Save collection statistics to log file"""
    try:
        log_file = LOGS_DIR / "collection.log"

        log_entry = (
            f"{datetime.now().isoformat()} | "
            f"Success: {stats['success']}/{stats['total']} | "
            f"Duration: {stats['duration']:.1f}s\n"
        )

        with open(log_file, 'a') as f:
            f.write(log_entry)

    except Exception as e:
        logger.error(f"Error saving collection log: {e}")


def main():
    """Main data collection routine"""
    logger.info("=" * 60)
    logger.info("Starting data collection")
    logger.info("=" * 60)

    start_time = time.time()

    # Check if market is open (optional - comment out to always collect)
    # if not is_market_hours():
    #     logger.info("Skipping collection - outside market hours")
    #     return 0

    # Get stock list
    stocks = get_stock_list()
    logger.info(f"Collecting data for {len(stocks)} stocks")

    # Collection statistics
    stats = {
        'total': len(stocks),
        'success': 0,
        'failed': 0,
        'duration': 0
    }

    # Collect data for each stock
    for symbol in stocks:
        try:
            # Get current quote
            quote = get_current_quote(symbol)
            if quote:
                stats['success'] += 1

                # Update predictions history
                update_predictions_history(quote)

                # Update historical data (less frequently in production)
                # For GitHub Actions, we do this every time to keep data fresh
                update_historical_data(symbol, days=730)
            else:
                stats['failed'] += 1

            # Rate limiting - be nice to Yahoo Finance
            time.sleep(1)

        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
            stats['failed'] += 1

    # Calculate duration
    stats['duration'] = time.time() - start_time

    # Log results
    logger.info("=" * 60)
    logger.info(f"Collection completed: {stats['success']}/{stats['total']} successful")
    logger.info(f"Duration: {stats['duration']:.1f} seconds")
    logger.info("=" * 60)

    # Save collection log
    save_collection_log(stats)

    # Exit with error code if all failed
    if stats['success'] == 0:
        logger.error("All collections failed!")
        return 1

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
