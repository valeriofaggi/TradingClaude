"""
Stock Price Prediction Models
Implements ensemble of ML models for stock price forecasting
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from prophet import Prophet
import logging
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockPredictor:
    """Ensemble predictor combining multiple ML models"""

    def __init__(self):
        """Initialize the predictor"""
        self.scaler = MinMaxScaler()
        self.prophet_model = None
        self.rf_model = None
        self.is_trained = False

    def prepare_data(self, df: pd.DataFrame, lookback: int = 60) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for training

        Args:
            df: DataFrame with historical data
            lookback: Number of days to look back

        Returns:
            X, y arrays for training
        """
        # Use closing price and technical indicators
        feature_columns = ['close']

        # Add technical indicators if available
        technical_features = ['RSI_14', 'MACD', 'SMA_20', 'SMA_50', 'volume']
        for feat in technical_features:
            if feat in df.columns:
                feature_columns.append(feat)

        # Extract features
        data = df[feature_columns].values

        # Handle NaN values
        data = np.nan_to_num(data, nan=0.0)

        # Scale data
        scaled_data = self.scaler.fit_transform(data)

        # Create sequences
        X, y = [], []
        for i in range(lookback, len(scaled_data)):
            X.append(scaled_data[i-lookback:i])
            y.append(scaled_data[i, 0])  # Predict close price

        return np.array(X), np.array(y)

    def train_prophet(self, df: pd.DataFrame) -> None:
        """
        Train Prophet model for time series forecasting

        Args:
            df: DataFrame with historical data
        """
        try:
            # Prepare data for Prophet (remove timezone if present)
            dates = df.index
            if hasattr(dates, 'tz') and dates.tz is not None:
                dates = dates.tz_localize(None)

            prophet_df = pd.DataFrame({
                'ds': dates,
                'y': df['close'].values
            })

            # Initialize and train Prophet
            self.prophet_model = Prophet(
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=True,
                changepoint_prior_scale=0.05
            )

            self.prophet_model.fit(prophet_df)
            logger.info("Prophet model trained successfully")

        except Exception as e:
            logger.error(f"Error training Prophet model: {e}")
            self.prophet_model = None

    def train_random_forest(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Train Random Forest model

        Args:
            X: Feature array
            y: Target array
        """
        try:
            # Reshape X for Random Forest (needs 2D input)
            X_reshaped = X.reshape(X.shape[0], -1)

            # Train Random Forest
            self.rf_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                random_state=42,
                n_jobs=-1
            )

            self.rf_model.fit(X_reshaped, y)
            logger.info("Random Forest model trained successfully")

        except Exception as e:
            logger.error(f"Error training Random Forest: {e}")
            self.rf_model = None

    def train(self, df: pd.DataFrame, lookback: int = 60) -> bool:
        """
        Train all models

        Args:
            df: DataFrame with historical data
            lookback: Number of days for lookback

        Returns:
            True if training successful
        """
        if df.empty or len(df) < lookback + 100:
            logger.error("Insufficient data for training")
            return False

        logger.info("Starting model training...")

        # Prepare data
        X, y = self.prepare_data(df, lookback)

        if len(X) == 0:
            logger.error("No data prepared for training")
            return False

        # Train Prophet
        self.train_prophet(df)

        # Train Random Forest
        self.train_random_forest(X, y)

        self.is_trained = True
        logger.info("All models trained successfully")
        return True

    def predict_prophet(self, days: int) -> Optional[pd.DataFrame]:
        """
        Make predictions using Prophet

        Args:
            days: Number of days to predict

        Returns:
            DataFrame with predictions
        """
        if not self.prophet_model:
            return None

        try:
            # Create future dataframe
            future = self.prophet_model.make_future_dataframe(periods=days)

            # Make predictions
            forecast = self.prophet_model.predict(future)

            return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days)

        except Exception as e:
            logger.error(f"Error in Prophet prediction: {e}")
            return None

    def predict_rf(self, last_sequence: np.ndarray, steps: int) -> Optional[np.ndarray]:
        """
        Make predictions using Random Forest

        Args:
            last_sequence: Last sequence of data
            steps: Number of steps to predict

        Returns:
            Array of predictions
        """
        if not self.rf_model:
            return None

        try:
            predictions = []
            current_sequence = last_sequence.copy()

            for _ in range(steps):
                # Reshape for prediction
                X_pred = current_sequence.reshape(1, -1)

                # Predict next value
                pred = self.rf_model.predict(X_pred)[0]
                predictions.append(pred)

                # Update sequence for next prediction
                current_sequence = np.roll(current_sequence, -1)
                current_sequence[-1] = pred

            return np.array(predictions)

        except Exception as e:
            logger.error(f"Error in RF prediction: {e}")
            return None

    def predict(self, df: pd.DataFrame, hours: int = 0, days: int = 1,
                sentiment_weight: float = 0.0) -> Dict:
        """
        Make ensemble predictions

        Args:
            df: DataFrame with historical data
            hours: Hours to predict (for intraday)
            days: Days to predict
            sentiment_weight: Sentiment adjustment (-1 to 1)

        Returns:
            Dictionary with predictions
        """
        if not self.is_trained:
            logger.error("Models not trained yet")
            return {}

        # Calculate total prediction steps
        total_days = days if hours == 0 else max(1, int(hours / 24))

        predictions = {
            'horizon': f"{hours}h" if hours > 0 else f"{days}d",
            'predictions': [],
            'confidence_lower': [],
            'confidence_upper': [],
            'model_weights': {}
        }

        # Prophet predictions
        prophet_pred = self.predict_prophet(total_days)

        # Random Forest predictions
        X_data = self.prepare_data(df.tail(60))[0]
        if len(X_data) > 0:
            last_sequence = X_data[-1]
            rf_pred = self.predict_rf(last_sequence, total_days)
        else:
            rf_pred = None

        # Ensemble predictions
        if prophet_pred is not None and rf_pred is not None:
            # Weight models (can be adjusted based on performance)
            prophet_weight = 0.6
            rf_weight = 0.4

            # Get Prophet predictions
            prophet_values = prophet_pred['yhat'].values

            # Inverse transform RF predictions
            rf_pred_full = np.zeros((len(rf_pred), self.scaler.n_features_in_))
            rf_pred_full[:, 0] = rf_pred
            rf_values = self.scaler.inverse_transform(rf_pred_full)[:, 0]

            # Ensemble combination
            ensemble_pred = (prophet_weight * prophet_values + rf_weight * rf_values)

            # Apply sentiment adjustment
            if sentiment_weight != 0:
                current_price = df['close'].iloc[-1]
                sentiment_adjustment = current_price * sentiment_weight * 0.02  # Max 2% adjustment
                ensemble_pred = ensemble_pred + sentiment_adjustment

            predictions['predictions'] = ensemble_pred.tolist()
            predictions['confidence_lower'] = prophet_pred['yhat_lower'].values.tolist()
            predictions['confidence_upper'] = prophet_pred['yhat_upper'].values.tolist()
            predictions['model_weights'] = {
                'prophet': prophet_weight,
                'random_forest': rf_weight,
                'sentiment': abs(sentiment_weight)
            }

        elif prophet_pred is not None:
            # Use only Prophet
            predictions['predictions'] = prophet_pred['yhat'].values.tolist()
            predictions['confidence_lower'] = prophet_pred['yhat_lower'].values.tolist()
            predictions['confidence_upper'] = prophet_pred['yhat_upper'].values.tolist()
            predictions['model_weights'] = {'prophet': 1.0}

        return predictions


if __name__ == "__main__":
    # Test the predictor
    import yfinance as yf
    from technical_indicators import TechnicalAnalyzer

    # Get test data
    ticker = yf.Ticker("ENI.MI")
    df = ticker.history(period="2y")
    df = df.rename(columns={
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    })

    # Add technical indicators
    analyzer = TechnicalAnalyzer()
    df = analyzer.calculate_all_indicators(df)

    # Train predictor
    predictor = StockPredictor()
    success = predictor.train(df)

    if success:
        # Make predictions
        pred_1d = predictor.predict(df, days=1)
        pred_7d = predictor.predict(df, days=7)

        print("\n1-Day Prediction:")
        print(pred_1d)
        print("\n7-Day Prediction:")
        print(pred_7d)
