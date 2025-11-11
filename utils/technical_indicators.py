"""
Technical Indicators Module
Calculate technical analysis indicators for stock data
"""

import pandas as pd
import numpy as np
from typing import Dict
import ta


class TechnicalAnalyzer:
    """Calculate technical indicators for stock data"""

    @staticmethod
    def calculate_sma(df: pd.DataFrame, periods: list = [20, 50, 200]) -> pd.DataFrame:
        """Calculate Simple Moving Averages"""
        for period in periods:
            df[f'SMA_{period}'] = df['close'].rolling(window=period).mean()
        return df

    @staticmethod
    def calculate_ema(df: pd.DataFrame, periods: list = [12, 26]) -> pd.DataFrame:
        """Calculate Exponential Moving Averages"""
        for period in periods:
            df[f'EMA_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
        return df

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Relative Strength Index"""
        df['RSI_14'] = ta.momentum.rsi(df['close'], window=period)
        return df

    @staticmethod
    def calculate_macd(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        macd = ta.trend.MACD(df['close'])
        df['MACD'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal()
        df['MACD_diff'] = macd.macd_diff()
        return df

    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        bb = ta.volatility.BollingerBands(df['close'], window=period)
        df['BB_UPPER'] = bb.bollinger_hband()
        df['BB_MIDDLE'] = bb.bollinger_mavg()
        df['BB_LOWER'] = bb.bollinger_lband()
        df['BB_WIDTH'] = bb.bollinger_wband()
        return df

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Average True Range"""
        df['ATR'] = ta.volatility.average_true_range(
            df['high'], df['low'], df['close'], window=period
        )
        return df

    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate On-Balance Volume"""
        df['OBV'] = ta.volume.on_balance_volume(df['close'], df['volume'])
        return df

    @staticmethod
    def calculate_stochastic(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Stochastic Oscillator"""
        stoch = ta.momentum.StochasticOscillator(
            df['high'], df['low'], df['close'], window=period
        )
        df['STOCH_K'] = stoch.stoch()
        df['STOCH_D'] = stoch.stoch_signal()
        return df

    @staticmethod
    def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Average Directional Index"""
        df['ADX'] = ta.trend.adx(df['high'], df['low'], df['close'], window=period)
        return df

    @staticmethod
    def calculate_cci(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Calculate Commodity Channel Index"""
        df['CCI'] = ta.trend.cci(df['high'], df['low'], df['close'], window=period)
        return df

    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with all indicators added
        """
        if df.empty or len(df) < 200:
            return df

        # Make a copy to avoid modifying original
        df = df.copy()

        # Moving Averages
        df = TechnicalAnalyzer.calculate_sma(df, [20, 50, 200])
        df = TechnicalAnalyzer.calculate_ema(df, [12, 26])

        # Momentum Indicators
        df = TechnicalAnalyzer.calculate_rsi(df)
        df = TechnicalAnalyzer.calculate_stochastic(df)
        df = TechnicalAnalyzer.calculate_cci(df)

        # Trend Indicators
        df = TechnicalAnalyzer.calculate_macd(df)
        df = TechnicalAnalyzer.calculate_adx(df)

        # Volatility Indicators
        df = TechnicalAnalyzer.calculate_bollinger_bands(df)
        df = TechnicalAnalyzer.calculate_atr(df)

        # Volume Indicators
        df = TechnicalAnalyzer.calculate_obv(df)

        return df

    @staticmethod
    def get_trading_signals(df: pd.DataFrame) -> Dict[str, str]:
        """
        Generate trading signals based on technical indicators

        Args:
            df: DataFrame with technical indicators

        Returns:
            Dictionary with signal interpretations
        """
        if df.empty or len(df) < 2:
            return {}

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        signals = {}

        # RSI Signal
        if 'RSI_14' in latest and not pd.isna(latest['RSI_14']):
            if latest['RSI_14'] < 30:
                signals['RSI'] = 'OVERSOLD - Possible Buy'
            elif latest['RSI_14'] > 70:
                signals['RSI'] = 'OVERBOUGHT - Possible Sell'
            else:
                signals['RSI'] = 'NEUTRAL'

        # MACD Signal
        if 'MACD' in latest and 'MACD_signal' in latest:
            if not pd.isna(latest['MACD']) and not pd.isna(prev['MACD']):
                if prev['MACD'] < prev['MACD_signal'] and latest['MACD'] > latest['MACD_signal']:
                    signals['MACD'] = 'BULLISH CROSSOVER - Buy Signal'
                elif prev['MACD'] > prev['MACD_signal'] and latest['MACD'] < latest['MACD_signal']:
                    signals['MACD'] = 'BEARISH CROSSOVER - Sell Signal'
                else:
                    signals['MACD'] = 'NEUTRAL'

        # Bollinger Bands Signal
        if all(k in latest for k in ['BB_UPPER', 'BB_LOWER', 'close']):
            if not pd.isna(latest['BB_UPPER']):
                if latest['close'] > latest['BB_UPPER']:
                    signals['BB'] = 'ABOVE UPPER BAND - Overbought'
                elif latest['close'] < latest['BB_LOWER']:
                    signals['BB'] = 'BELOW LOWER BAND - Oversold'
                else:
                    signals['BB'] = 'WITHIN BANDS - Normal'

        # Moving Average Signal
        if all(k in latest for k in ['SMA_20', 'SMA_50', 'close']):
            if not pd.isna(latest['SMA_20']) and not pd.isna(latest['SMA_50']):
                if latest['SMA_20'] > latest['SMA_50'] and latest['close'] > latest['SMA_20']:
                    signals['MA'] = 'BULLISH - Price above MAs'
                elif latest['SMA_20'] < latest['SMA_50'] and latest['close'] < latest['SMA_20']:
                    signals['MA'] = 'BEARISH - Price below MAs'
                else:
                    signals['MA'] = 'MIXED'

        return signals


if __name__ == "__main__":
    # Test technical indicators
    import yfinance as yf

    ticker = yf.Ticker("ENI.MI")
    df = ticker.history(period="6mo")
    df = df.rename(columns={
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    })

    analyzer = TechnicalAnalyzer()
    df = analyzer.calculate_all_indicators(df)
    signals = analyzer.get_trading_signals(df)

    print("Technical Indicators calculated:")
    print(df[['close', 'RSI_14', 'MACD', 'BB_UPPER', 'BB_LOWER']].tail())
    print("\nTrading Signals:")
    for indicator, signal in signals.items():
        print(f"{indicator}: {signal}")
