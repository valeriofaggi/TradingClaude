"""
Prediction Logger Module
Stores predictions to track accuracy over time
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PredictionLogger:
    """Logs predictions and compares them with actual values"""

    def __init__(self, data_dir: Path):
        """
        Initialize prediction logger

        Args:
            data_dir: Directory to store prediction logs
        """
        self.data_dir = data_dir
        self.predictions_file = data_dir / "predictions_history.csv"

        # Create predictions file if it doesn't exist
        if not self.predictions_file.exists():
            self._initialize_predictions_file()

    def _initialize_predictions_file(self):
        """Create empty predictions CSV file with headers"""
        df = pd.DataFrame(columns=[
            'prediction_timestamp',  # When prediction was made
            'symbol',                # Stock symbol
            'stock_name',            # Full company name
            'current_price',         # Price at prediction time
            'horizon',               # Forecast horizon (2h, 1d, 3d, 7d)
            'target_timestamp',      # When prediction is for
            'predicted_price',       # Predicted price
            'predicted_change_pct',  # Predicted % change
            'actual_price',          # Actual price (filled later)
            'actual_change_pct',     # Actual % change (filled later)
            'error_pct',             # Prediction error % (filled later)
            'accuracy_evaluated'     # Whether actual values have been filled
        ])
        df.to_csv(self.predictions_file, index=False)
        logger.info(f"Initialized predictions file: {self.predictions_file}")

    def log_prediction(self, symbol: str, stock_name: str, current_price: float,
                       horizon: str, predicted_price: float) -> None:
        """
        Log a prediction

        Args:
            symbol: Stock symbol
            stock_name: Full company name
            current_price: Current price
            horizon: Forecast horizon (2h, 1d, 3d, 7d)
            predicted_price: Predicted price
        """
        try:
            # Calculate target timestamp based on horizon
            prediction_time = datetime.now()

            if 'h' in horizon:
                hours = int(horizon.replace('h', ''))
                target_time = prediction_time + timedelta(hours=hours)
            elif 'd' in horizon:
                days = int(horizon.replace('d', ''))
                target_time = prediction_time + timedelta(days=days)
            else:
                logger.warning(f"Unknown horizon format: {horizon}")
                return

            # Calculate predicted change percentage
            predicted_change_pct = ((predicted_price - current_price) / current_price) * 100

            # Create prediction record
            prediction_record = {
                'prediction_timestamp': prediction_time.strftime('%Y-%m-%d %H:%M:%S'),
                'symbol': symbol,
                'stock_name': stock_name,
                'current_price': round(current_price, 4),
                'horizon': horizon,
                'target_timestamp': target_time.strftime('%Y-%m-%d %H:%M:%S'),
                'predicted_price': round(predicted_price, 4),
                'predicted_change_pct': round(predicted_change_pct, 2),
                'actual_price': None,
                'actual_change_pct': None,
                'error_pct': None,
                'accuracy_evaluated': False
            }

            # Append to CSV
            df = pd.DataFrame([prediction_record])
            df.to_csv(self.predictions_file, mode='a', header=False, index=False)

            logger.info(f"Logged prediction for {symbol} ({horizon}): {predicted_price:.2f}")

        except Exception as e:
            logger.error(f"Error logging prediction: {e}")

    def update_actual_values(self, current_prices: Dict[str, float]) -> int:
        """
        Update predictions with actual values for completed forecasts

        Args:
            current_prices: Dictionary of symbol -> current price

        Returns:
            Number of predictions updated
        """
        try:
            # Load predictions
            df = pd.read_csv(self.predictions_file)

            if df.empty:
                return 0

            # Convert timestamps
            df['prediction_timestamp'] = pd.to_datetime(df['prediction_timestamp'])
            df['target_timestamp'] = pd.to_datetime(df['target_timestamp'])

            current_time = datetime.now()
            updated_count = 0

            # Find predictions that should be evaluated
            mask = (df['target_timestamp'] <= current_time) & (df['accuracy_evaluated'] == False)
            predictions_to_update = df[mask]

            for idx, row in predictions_to_update.iterrows():
                symbol = row['symbol']

                if symbol in current_prices:
                    actual_price = current_prices[symbol]
                    current_price = row['current_price']

                    # Calculate actual change
                    actual_change_pct = ((actual_price - current_price) / current_price) * 100

                    # Calculate error
                    predicted_price = row['predicted_price']
                    error_pct = abs(((actual_price - predicted_price) / actual_price) * 100)

                    # Update dataframe
                    df.at[idx, 'actual_price'] = round(actual_price, 4)
                    df.at[idx, 'actual_change_pct'] = round(actual_change_pct, 2)
                    df.at[idx, 'error_pct'] = round(error_pct, 2)
                    df.at[idx, 'accuracy_evaluated'] = True

                    updated_count += 1

            # Save updated predictions
            if updated_count > 0:
                df.to_csv(self.predictions_file, index=False)
                logger.info(f"Updated {updated_count} predictions with actual values")

            return updated_count

        except Exception as e:
            logger.error(f"Error updating actual values: {e}")
            return 0

    def get_accuracy_stats(self, symbol: Optional[str] = None,
                          horizon: Optional[str] = None) -> Dict:
        """
        Get accuracy statistics

        Args:
            symbol: Filter by symbol (optional)
            horizon: Filter by horizon (optional)

        Returns:
            Dictionary with accuracy metrics
        """
        try:
            df = pd.read_csv(self.predictions_file)

            if df.empty:
                return {'total_predictions': 0, 'evaluated_predictions': 0}

            # Filter by symbol and horizon if specified
            if symbol:
                df = df[df['symbol'] == symbol]
            if horizon:
                df = df[df['horizon'] == horizon]

            # Filter only evaluated predictions
            evaluated_df = df[df['accuracy_evaluated'] == True]

            if evaluated_df.empty:
                return {
                    'total_predictions': len(df),
                    'evaluated_predictions': 0,
                    'average_error_pct': None,
                    'median_error_pct': None,
                    'correct_direction_pct': None
                }

            # Calculate metrics
            avg_error = evaluated_df['error_pct'].mean()
            median_error = evaluated_df['error_pct'].median()

            # Calculate direction accuracy (did we predict up/down correctly?)
            correct_direction = sum(
                (evaluated_df['predicted_change_pct'] > 0) == (evaluated_df['actual_change_pct'] > 0)
            )
            direction_accuracy = (correct_direction / len(evaluated_df)) * 100

            return {
                'total_predictions': len(df),
                'evaluated_predictions': len(evaluated_df),
                'average_error_pct': round(avg_error, 2),
                'median_error_pct': round(median_error, 2),
                'correct_direction_pct': round(direction_accuracy, 2),
                'best_prediction_error': round(evaluated_df['error_pct'].min(), 2),
                'worst_prediction_error': round(evaluated_df['error_pct'].max(), 2)
            }

        except Exception as e:
            logger.error(f"Error calculating accuracy stats: {e}")
            return {'error': str(e)}

    def get_predictions_history(self, symbol: Optional[str] = None,
                               limit: int = 100) -> pd.DataFrame:
        """
        Get predictions history

        Args:
            symbol: Filter by symbol (optional)
            limit: Maximum number of records to return

        Returns:
            DataFrame with predictions history
        """
        try:
            df = pd.read_csv(self.predictions_file)

            if df.empty:
                return pd.DataFrame()

            # Filter by symbol if specified
            if symbol:
                df = df[df['symbol'] == symbol]

            # Sort by timestamp (most recent first)
            df['prediction_timestamp'] = pd.to_datetime(df['prediction_timestamp'])
            df = df.sort_values('prediction_timestamp', ascending=False)

            # Limit results
            df = df.head(limit)

            return df

        except Exception as e:
            logger.error(f"Error getting predictions history: {e}")
            return pd.DataFrame()

    def get_accuracy_by_horizon(self) -> pd.DataFrame:
        """
        Get accuracy metrics grouped by forecast horizon

        Returns:
            DataFrame with accuracy by horizon
        """
        try:
            df = pd.read_csv(self.predictions_file)

            if df.empty:
                return pd.DataFrame()

            # Filter only evaluated predictions
            evaluated_df = df[df['accuracy_evaluated'] == True]

            if evaluated_df.empty:
                return pd.DataFrame()

            # Group by horizon
            accuracy_by_horizon = evaluated_df.groupby('horizon').agg({
                'error_pct': ['mean', 'median', 'min', 'max', 'count'],
                'predicted_change_pct': lambda x: sum((x > 0) == (evaluated_df.loc[x.index, 'actual_change_pct'] > 0)) / len(x) * 100
            }).round(2)

            accuracy_by_horizon.columns = ['Errore Medio %', 'Errore Mediano %',
                                          'Miglior Errore %', 'Peggior Errore %',
                                          'N. Previsioni', 'Direzione Corretta %']

            return accuracy_by_horizon.reset_index().rename(columns={'horizon': 'Orizzonte'})

        except Exception as e:
            logger.error(f"Error calculating accuracy by horizon: {e}")
            return pd.DataFrame()


if __name__ == "__main__":
    # Test the logger
    from config.config import DATA_DIR

    logger_test = PredictionLogger(DATA_DIR)

    # Log some test predictions
    logger_test.log_prediction("ENI.MI", "Eni S.p.A.", 14.50, "1d", 14.75)
    logger_test.log_prediction("ENI.MI", "Eni S.p.A.", 14.50, "3d", 15.00)

    # Get history
    history = logger_test.get_predictions_history()
    print("\nPredictions History:")
    print(history)

    # Get stats
    stats = logger_test.get_accuracy_stats()
    print("\nAccuracy Stats:")
    print(stats)
