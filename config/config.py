# Configuration file for Trading Predictor
import os
from pathlib import Path
from dotenv import load_dotenv

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

# API Configuration
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")  # Inserire la tua API key

# Top 10 most traded Italian stocks (FTSE MIB components)
TOP_ITALIAN_STOCKS = [
    "ENI.MI",          # Eni
    "ISP.MI",          # Intesa Sanpaolo
    "UCG.MI",          # UniCredit
    "ENEL.MI",         # Enel
    "A2A.MI",          # A2A (sostituisce STM.MI)
    "TIT.MI",          # Telecom Italia
    "G.MI",            # Generali
    "RACE.MI",         # Ferrari
    "BAMI.MI",         # Banco BPM (sostituisce STLA.MI)
    "TEN.MI",          # Tenaris
]

# Nomi completi delle società
STOCK_NAMES = {
    "ENI.MI": "Eni S.p.A.",
    "ISP.MI": "Intesa Sanpaolo S.p.A.",
    "UCG.MI": "UniCredit S.p.A.",
    "ENEL.MI": "Enel S.p.A.",
    "A2A.MI": "A2A S.p.A.",
    "TIT.MI": "TIM S.p.A. (Telecom Italia)",
    "G.MI": "Assicurazioni Generali S.p.A.",
    "RACE.MI": "Ferrari N.V.",
    "BAMI.MI": "Banco BPM S.p.A.",
    "TEN.MI": "Tenaris S.A.",
}

# Alternative symbols for Yahoo Finance (backup)
YAHOO_SYMBOLS = [symbol for symbol in TOP_ITALIAN_STOCKS]

# Data collection settings
DATA_COLLECTION = {
    "historical_days": 730,  # 2 years of historical data
    "update_interval": 900,  # Update every 15 minutes (900 seconds)
    "max_retries": 3,
    "retry_delay": 5,
}

# ML Model settings
ML_CONFIG = {
    "train_test_split": 0.8,
    "validation_split": 0.1,
    "lookback_period": 60,  # days for LSTM
    "forecast_horizons": {
        "2h": 2,      # 2 hours
        "1d": 1,      # 1 day
        "3d": 3,      # 3 days
        "7d": 7,      # 7 days
    }
}

# Technical indicators to calculate
TECHNICAL_INDICATORS = [
    "SMA_20", "SMA_50", "SMA_200",  # Simple Moving Averages
    "EMA_12", "EMA_26",              # Exponential Moving Averages
    "RSI_14",                        # Relative Strength Index
    "MACD",                          # Moving Average Convergence Divergence
    "BB_UPPER", "BB_LOWER",          # Bollinger Bands
    "ATR",                           # Average True Range
    "OBV",                           # On-Balance Volume
]

# News sentiment analysis
NEWS_CONFIG = {
    "max_news_per_stock": 20,
    "sentiment_weight": 0.3,  # Weight in prediction (30%)
    "news_lookback_days": 7,
}

# Dashboard settings
DASHBOARD_CONFIG = {
    "title": "Trading Predictor",
    "refresh_interval": 900,  # 15 minutes
    "chart_height": 600,
    "show_confidence_intervals": True,
}

# Logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_file": LOGS_DIR / "trading_predictor.log",
}
