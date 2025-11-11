"""
Trading Predictor - Streamlit Dashboard
Main application with multi-page support for different time horizons
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path
from datetime import datetime, timedelta
import time
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config.config import (
    TOP_ITALIAN_STOCKS, STOCK_NAMES, FINNHUB_API_KEY, DATA_DIR,
    DASHBOARD_CONFIG, ML_CONFIG
)
from utils.data_collector import DataCollector
from utils.technical_indicators import TechnicalAnalyzer
from utils.sentiment_analyzer import SentimentAnalyzer
from utils.prediction_logger import PredictionLogger
from models.predictor import StockPredictor
from sync_data import sync_from_github, get_sync_status

# Page configuration
st.set_page_config(
    page_title="Trading Predictor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .positive {
        color: #00cc00;
    }
    .negative {
        color: #ff0000;
    }

    /* Tab navigation improvements - scrollable with arrows */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        overflow-x: auto;
        overflow-y: hidden;
        white-space: nowrap;
        scrollbar-width: thin;
        scrollbar-color: #888 #f0f2f6;
        padding: 0.5rem 0;
    }

    /* Scrollbar styling for webkit browsers */
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
        height: 8px;
    }

    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-track {
        background: #f0f2f6;
        border-radius: 10px;
    }

    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 10px;
    }

    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb:hover {
        background: #555;
    }

    /* Make tabs more compact */
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
        white-space: nowrap;
    }
</style>
""", unsafe_allow_html=True)


class TradingDashboard:
    """Main dashboard class"""

    def __init__(self):
        """Initialize dashboard"""
        self.initialize_session_state()
        self.data_collector = DataCollector(FINNHUB_API_KEY, DATA_DIR)
        self.technical_analyzer = TechnicalAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.predictor = StockPredictor()
        self.prediction_logger = PredictionLogger(DATA_DIR)

    @staticmethod
    def initialize_session_state():
        """Initialize Streamlit session state"""
        if 'data_loaded' not in st.session_state:
            st.session_state.data_loaded = False
        if 'selected_stock' not in st.session_state:
            st.session_state.selected_stock = TOP_ITALIAN_STOCKS[0]
        if 'last_update' not in st.session_state:
            st.session_state.last_update = None
        if 'stock_data' not in st.session_state:
            st.session_state.stock_data = {}
        if 'predictions' not in st.session_state:
            st.session_state.predictions = {}
        if 'auto_refresh_enabled' not in st.session_state:
            st.session_state.auto_refresh_enabled = True
        if 'auto_refresh_interval' not in st.session_state:
            st.session_state.auto_refresh_interval = 5  # minuti
        if 'next_refresh_time' not in st.session_state:
            st.session_state.next_refresh_time = None
        # Nuove variabili per l'aggiornamento automatico di tutti i titoli
        if 'all_stocks_loaded' not in st.session_state:
            st.session_state.all_stocks_loaded = False
        if 'stock_predictions' not in st.session_state:
            st.session_state.stock_predictions = {}  # {symbol: {horizon: predictions}}
        if 'last_full_update' not in st.session_state:
            st.session_state.last_full_update = None
        if 'update_in_progress' not in st.session_state:
            st.session_state.update_in_progress = False
        # Gestione titoli personalizzati
        if 'custom_stocks' not in st.session_state:
            st.session_state.custom_stocks = None  # Caricato al primo avvio
        if 'active_stocks' not in st.session_state:
            st.session_state.active_stocks = TOP_ITALIAN_STOCKS.copy()

    def get_custom_stocks_file(self):
        """Ottieni il percorso del file dei titoli personalizzati"""
        return DATA_DIR / "custom_stocks.json"

    def load_custom_stocks(self):
        """Carica la lista di titoli personalizzati dal file JSON"""
        custom_file = self.get_custom_stocks_file()
        if custom_file.exists():
            try:
                with open(custom_file, 'r') as f:
                    data = json.load(f)
                    st.session_state.custom_stocks = data.get('stocks', [])
                    st.session_state.active_stocks = st.session_state.custom_stocks.copy()
                    return True
            except Exception as e:
                st.error(f"Errore nel caricamento dei titoli personalizzati: {e}")
                return False
        return False

    def save_custom_stocks(self):
        """Salva la lista di titoli personalizzati nel file JSON"""
        custom_file = self.get_custom_stocks_file()
        try:
            data = {
                'stocks': st.session_state.active_stocks,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            with open(custom_file, 'w') as f:
                json.dump(data, f, indent=2)
            st.session_state.custom_stocks = st.session_state.active_stocks.copy()
            return True
        except Exception as e:
            st.error(f"Errore nel salvataggio dei titoli personalizzati: {e}")
            return False

    def validate_stock_symbol(self, symbol: str) -> bool:
        """Valida un simbolo di titolo provando a recuperare i dati"""
        try:
            # Prova a ottenere un quote per il simbolo
            quote = self.data_collector.get_stock_quote(symbol)
            if quote and quote.get('current_price', 0) > 0:
                return True
            return False
        except Exception:
            return False

    def get_active_stocks(self):
        """Ottieni la lista attiva di titoli"""
        return st.session_state.active_stocks

    def load_data(self, symbol: str, force_refresh: bool = False):
        """Carica i dati per un titolo specifico"""
        # Controlla se è necessario aggiornare
        if (not force_refresh and
            symbol in st.session_state.stock_data and
            st.session_state.last_update):
            time_since_update = (datetime.now() - st.session_state.last_update).seconds
            if time_since_update < DASHBOARD_CONFIG['refresh_interval']:
                return st.session_state.stock_data[symbol]

        with st.spinner(f'Caricamento dati per {symbol}...'):
            # Ottieni dati storici
            hist_df = self.data_collector.get_historical_data(symbol, days=730)

            if hist_df.empty:
                st.error(f"Nessun dato disponibile per {symbol}")
                return None

            # Calculate technical indicators
            hist_df = self.technical_analyzer.calculate_all_indicators(hist_df)

            # Get current quote
            quote = self.data_collector.get_stock_quote(symbol)

            # Update actual values for past predictions
            if quote:
                current_prices = {symbol: quote['current_price']}
                self.prediction_logger.update_actual_values(current_prices)

            # Get news and sentiment
            news = self.data_collector.get_company_news(symbol, days=7)
            sentiment = self.sentiment_analyzer.analyze_news_list(news)

            # Store in session state
            st.session_state.stock_data[symbol] = {
                'historical': hist_df,
                'quote': quote,
                'news': news,
                'sentiment': sentiment
            }
            st.session_state.last_update = datetime.now()

            # Imposta il prossimo refresh se auto-refresh è abilitato
            if st.session_state.auto_refresh_enabled:
                st.session_state.next_refresh_time = datetime.now() + timedelta(
                    minutes=st.session_state.auto_refresh_interval
                )

            return st.session_state.stock_data[symbol]

    def train_model(self, symbol: str):
        """Addestra il modello di previsione per un titolo"""
        if symbol not in st.session_state.stock_data:
            return False

        data = st.session_state.stock_data[symbol]
        hist_df = data['historical']

        with st.spinner('Addestramento modelli di previsione...'):
            success = self.predictor.train(hist_df)

        return success

    def make_predictions(self, symbol: str, hours: int = 0, days: int = 1):
        """Make predictions for a stock"""
        if symbol not in st.session_state.stock_data:
            return None

        data = st.session_state.stock_data[symbol]
        sentiment_weight = self.sentiment_analyzer.get_sentiment_weight(
            data['sentiment']
        )

        predictions = self.predictor.predict(
            data['historical'],
            hours=hours,
            days=days,
            sentiment_weight=sentiment_weight
        )

        # Log the prediction
        if predictions and 'predictions' in predictions and len(predictions['predictions']) > 0:
            current_price = data['quote']['current_price']
            predicted_price = predictions['predictions'][-1]  # Last prediction in the series

            # Determine horizon string
            horizon = f"{hours}h" if hours > 0 else f"{days}d"

            # Log to history
            self.prediction_logger.log_prediction(
                symbol=symbol,
                stock_name=STOCK_NAMES.get(symbol, symbol),
                current_price=current_price,
                horizon=horizon,
                predicted_price=predicted_price
            )

        return predictions

    def load_all_stocks_data(self, force_refresh: bool = False):
        """Carica dati e genera previsioni per tutti i titoli automaticamente"""
        # Controlla se è necessario aggiornare
        if (not force_refresh and
            st.session_state.all_stocks_loaded and
            st.session_state.last_full_update):
            time_since_update = (datetime.now() - st.session_state.last_full_update).seconds
            if time_since_update < DASHBOARD_CONFIG['refresh_interval']:
                return  # Dati già aggiornati

        # Evita aggiornamenti multipli in parallelo
        if st.session_state.update_in_progress:
            return

        st.session_state.update_in_progress = True

        try:
            # Definisci gli orizzonti temporali
            horizons = [
                {'hours': 2, 'days': 0, 'label': '2h'},
                {'hours': 0, 'days': 1, 'label': '1d'},
                {'hours': 0, 'days': 3, 'label': '3d'},
                {'hours': 0, 'days': 7, 'label': '7d'}
            ]

            progress_text = "Caricamento dati per tutti i titoli..."
            progress_bar = st.progress(0, text=progress_text)

            active_stocks = self.get_active_stocks()
            total_stocks = len(active_stocks)

            for idx, symbol in enumerate(active_stocks):
                # Aggiorna progress bar
                progress = (idx + 1) / total_stocks
                progress_bar.progress(progress, text=f"Elaborazione {symbol} ({idx + 1}/{total_stocks})...")

                # Carica dati del titolo
                self.load_data(symbol, force_refresh=force_refresh)

                if symbol not in st.session_state.stock_data:
                    continue

                # Addestra modello
                if not self.train_model(symbol):
                    continue

                # Genera previsioni per tutti gli orizzonti
                if symbol not in st.session_state.stock_predictions:
                    st.session_state.stock_predictions[symbol] = {}

                for horizon in horizons:
                    predictions = self.make_predictions(
                        symbol,
                        hours=horizon['hours'],
                        days=horizon['days']
                    )
                    if predictions:
                        st.session_state.stock_predictions[symbol][horizon['label']] = predictions

            # Marca come completato
            st.session_state.all_stocks_loaded = True
            st.session_state.last_full_update = datetime.now()

            # Imposta il prossimo refresh
            if st.session_state.auto_refresh_enabled:
                st.session_state.next_refresh_time = datetime.now() + timedelta(
                    minutes=st.session_state.auto_refresh_interval
                )

            progress_bar.progress(1.0, text="✅ Caricamento completato!")
            time.sleep(1)
            progress_bar.empty()

        finally:
            st.session_state.update_in_progress = False

    @staticmethod
    def get_trend(current_price: float, predicted_price: float, threshold: float = 0.5) -> dict:
        """
        Determina il trend previsto (rialzo/ribasso/stabile)

        Args:
            current_price: Prezzo corrente
            predicted_price: Prezzo previsto
            threshold: Soglia percentuale per considerare stabile (default 0.5%)

        Returns:
            Dict con trend, variazione percentuale, emoji e colore
        """
        change_percent = ((predicted_price - current_price) / current_price) * 100

        if abs(change_percent) < threshold:
            return {
                'trend': 'Stabile',
                'emoji': '→',
                'color': 'gray',
                'change_percent': change_percent
            }
        elif change_percent > 0:
            return {
                'trend': 'Rialzo',
                'emoji': '↑',
                'color': 'green',
                'change_percent': change_percent
            }
        else:
            return {
                'trend': 'Ribasso',
                'emoji': '↓',
                'color': 'red',
                'change_percent': change_percent
            }

    def get_all_stocks_overview(self):
        """
        Ottiene la panoramica di tutti i titoli con previsioni per tutti i periodi
        Usa dati pre-calcolati per performance ottimali

        Returns:
            DataFrame con tutti i titoli e i loro trend previsti
        """
        overview_data = []

        # Mapping tra label usati nelle previsioni e quelli da visualizzare
        period_mapping = {
            '2h': '2 Ore',
            '1d': '1 Giorno',
            '3d': '3 Giorni',
            '7d': '7 Giorni'
        }

        periods_display = ['2 Ore', '1 Giorno', '3 Giorni', '7 Giorni']

        for symbol in self.get_active_stocks():
            row = {
                'Simbolo': symbol,
                'Nome': STOCK_NAMES.get(symbol, symbol)
            }

            # Usa i dati pre-calcolati
            if symbol in st.session_state.stock_data:
                data = st.session_state.stock_data[symbol]
                quote = data.get('quote')

                if quote:
                    current_price = quote['current_price']
                    row['Prezzo'] = f"€{current_price:.2f}"

                    # Usa le previsioni pre-calcolate
                    if symbol in st.session_state.stock_predictions:
                        symbol_predictions = st.session_state.stock_predictions[symbol]

                        for horizon_key, period_label in period_mapping.items():
                            if horizon_key in symbol_predictions:
                                predictions = symbol_predictions[horizon_key]

                                if predictions and 'predictions' in predictions and len(predictions['predictions']) > 0:
                                    predicted_price = predictions['predictions'][-1]
                                    trend = self.get_trend(current_price, predicted_price)
                                    row[period_label] = f"{trend['emoji']} {trend['change_percent']:+.2f}%"
                                else:
                                    row[period_label] = 'N/D'
                            else:
                                row[period_label] = 'Calcolo...'
                    else:
                        # Nessuna previsione disponibile
                        for period_label in periods_display:
                            row[period_label] = 'In attesa...'
                else:
                    # Nessuna quotazione disponibile
                    row['Prezzo'] = 'N/D'
                    for period_label in periods_display:
                        row[period_label] = 'N/D'
            else:
                # Nessun dato disponibile
                row['Prezzo'] = 'Caricamento...'
                for period_label in periods_display:
                    row[period_label] = 'Caricamento...'

            overview_data.append(row)

        return pd.DataFrame(overview_data)

    def plot_price_chart(self, symbol: str, days: int = 90):
        """Crea il grafico dei prezzi con indicatori tecnici"""
        if symbol not in st.session_state.stock_data:
            return None

        data = st.session_state.stock_data[symbol]
        df = data['historical'].tail(days)

        # Crea subplots
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Prezzo & Medie Mobili', 'RSI', 'MACD'),
            row_heights=[0.6, 0.2, 0.2]
        )

        # Grafico candlestick
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Prezzo'
        ), row=1, col=1)

        # Moving averages
        if 'SMA_20' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['SMA_20'],
                name='SMA 20', line=dict(color='orange', width=1)
            ), row=1, col=1)

        if 'SMA_50' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['SMA_50'],
                name='SMA 50', line=dict(color='blue', width=1)
            ), row=1, col=1)

        # RSI
        if 'RSI_14' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['RSI_14'],
                name='RSI', line=dict(color='purple', width=2)
            ), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

        # MACD
        if 'MACD' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['MACD'],
                name='MACD', line=dict(color='blue', width=2)
            ), row=3, col=1)
            if 'MACD_signal' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.index, y=df['MACD_signal'],
                    name='Signal', line=dict(color='red', width=2)
                ), row=3, col=1)

        # Update layout
        fig.update_layout(
            height=DASHBOARD_CONFIG['chart_height'],
            showlegend=True,
            xaxis_rangeslider_visible=False,
            title=f"{symbol} - Technical Analysis"
        )

        return fig

    def plot_prediction_chart(self, symbol: str, predictions: dict, actual_df: pd.DataFrame):
        """Crea il grafico delle previsioni"""
        if not predictions or 'predictions' not in predictions:
            return None

        fig = go.Figure()

        # Prezzi storici (ultimi 30 giorni)
        hist_df = actual_df.tail(30)
        fig.add_trace(go.Scatter(
            x=hist_df.index,
            y=hist_df['close'],
            mode='lines',
            name='Prezzo Storico',
            line=dict(color='blue', width=2)
        ))

        # Crea date future
        last_date = hist_df.index[-1]
        horizon = predictions['horizon']
        if 'h' in horizon:
            # Previsione ore (approssimata)
            future_dates = pd.date_range(
                start=last_date,
                periods=len(predictions['predictions']) + 1,
                freq='H'
            )[1:]
        else:
            # Previsione giorni
            future_dates = pd.date_range(
                start=last_date,
                periods=len(predictions['predictions']) + 1,
                freq='D'
            )[1:]

        # Prezzi previsti
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=predictions['predictions'],
            mode='lines+markers',
            name='Prezzo Previsto',
            line=dict(color='red', width=2, dash='dash')
        ))

        # Intervalli di confidenza
        if DASHBOARD_CONFIG['show_confidence_intervals']:
            if 'confidence_upper' in predictions:
                fig.add_trace(go.Scatter(
                    x=future_dates,
                    y=predictions['confidence_upper'],
                    fill=None,
                    mode='lines',
                    line_color='rgba(255,0,0,0.2)',
                    name='Confidenza Superiore'
                ))

            if 'confidence_lower' in predictions:
                fig.add_trace(go.Scatter(
                    x=future_dates,
                    y=predictions['confidence_lower'],
                    fill='tonexty',
                    mode='lines',
                    line_color='rgba(255,0,0,0.2)',
                    name='Confidenza Inferiore'
                ))

        fig.update_layout(
            title=f"{symbol} - Previsione {horizon}",
            xaxis_title="Data",
            yaxis_title="Prezzo (EUR)",
            height=500,
            showlegend=True
        )

        return fig

    def plot_prediction_accuracy_chart(self, symbol: str, horizon: str):
        """Crea grafico di confronto tra previsioni e valori reali"""
        # Mappa orizzonte a formato nel database
        horizon_map = {
            '2h': '2h',
            '1d': '1d',
            '3d': '3d',
            '7d': '7d'
        }

        db_horizon = horizon_map.get(horizon)
        if not db_horizon:
            return None

        # Ottieni storico previsioni per questo orizzonte e simbolo
        history = self.prediction_logger.get_predictions_history(symbol=symbol, limit=50)

        if history.empty:
            return None

        # Filtra per orizzonte specifico e solo previsioni valutate
        history = history[history['horizon'] == db_horizon]
        history = history[history['accuracy_evaluated'] == True]

        if history.empty:
            return None

        # Crea il grafico
        fig = go.Figure()

        # Converti timestamp
        history['target_timestamp'] = pd.to_datetime(history['target_timestamp'])
        history = history.sort_values('target_timestamp')

        # Linea prezzi previsti
        fig.add_trace(go.Scatter(
            x=history['target_timestamp'],
            y=history['predicted_price'],
            mode='lines+markers',
            name='Prezzo Previsto',
            line=dict(color='red', width=2),
            marker=dict(size=6)
        ))

        # Linea prezzi reali
        fig.add_trace(go.Scatter(
            x=history['target_timestamp'],
            y=history['actual_price'],
            mode='lines+markers',
            name='Prezzo Reale',
            line=dict(color='green', width=2),
            marker=dict(size=6)
        ))

        # Evidenzia errori con barre
        for idx, row in history.iterrows():
            color = 'rgba(255, 0, 0, 0.3)' if row['predicted_price'] > row['actual_price'] else 'rgba(0, 255, 0, 0.3)'
            fig.add_trace(go.Scatter(
                x=[row['target_timestamp'], row['target_timestamp']],
                y=[row['predicted_price'], row['actual_price']],
                mode='lines',
                line=dict(color=color, width=1),
                showlegend=False,
                hoverinfo='skip'
            ))

        fig.update_layout(
            title=f"{symbol} - Confronto Previsioni vs Reali (Orizzonte: {horizon})",
            xaxis_title="Data Obiettivo",
            yaxis_title="Prezzo (EUR)",
            height=500,
            showlegend=True,
            hovermode='x unified'
        )

        return fig

    def plot_prediction_error_chart(self, symbol: str, horizon: str):
        """Crea grafico dell'errore di previsione nel tempo"""
        # Mappa orizzonte
        horizon_map = {
            '2h': '2h',
            '1d': '1d',
            '3d': '3d',
            '7d': '7d'
        }

        db_horizon = horizon_map.get(horizon)
        if not db_horizon:
            return None

        # Ottieni storico previsioni
        history = self.prediction_logger.get_predictions_history(symbol=symbol, limit=50)

        if history.empty:
            return None

        # Filtra per orizzonte e valutate
        history = history[history['horizon'] == db_horizon]
        history = history[history['accuracy_evaluated'] == True]

        if history.empty:
            return None

        # Crea grafico
        fig = go.Figure()

        # Converti timestamp
        history['target_timestamp'] = pd.to_datetime(history['target_timestamp'])
        history = history.sort_values('target_timestamp')

        # Barre errore percentuale
        colors = ['red' if e > 5 else 'orange' if e > 2 else 'green' for e in history['error_pct']]

        fig.add_trace(go.Bar(
            x=history['target_timestamp'],
            y=history['error_pct'],
            name='Errore %',
            marker=dict(color=colors),
            text=history['error_pct'].round(2),
            textposition='outside'
        ))

        # Linea media errore
        avg_error = history['error_pct'].mean()
        fig.add_hline(
            y=avg_error,
            line_dash="dash",
            line_color="blue",
            annotation_text=f"Media: {avg_error:.2f}%"
        )

        fig.update_layout(
            title=f"{symbol} - Errore di Previsione nel Tempo (Orizzonte: {horizon})",
            xaxis_title="Data Obiettivo",
            yaxis_title="Errore %",
            height=400,
            showlegend=False
        )

        return fig

    def render_sidebar(self):
        """Renderizza la barra laterale con i controlli"""
        st.sidebar.markdown("# 📊 Controlli")

        # Selettore titolo con nomi completi
        active_stocks = self.get_active_stocks()
        stock_options = [f"{symbol} - {STOCK_NAMES.get(symbol, symbol)}" for symbol in active_stocks]

        # Controlla se il titolo selezionato è ancora nella lista
        if st.session_state.selected_stock not in active_stocks:
            st.session_state.selected_stock = active_stocks[0] if active_stocks else None

        current_index = active_stocks.index(st.session_state.selected_stock) if st.session_state.selected_stock in active_stocks else 0

        selected_option = st.sidebar.selectbox(
            "Seleziona Titolo",
            stock_options,
            index=current_index
        )

        # Estrai il simbolo dalla selezione (es: "ENI.MI - Eni S.p.A." -> "ENI.MI")
        selected_stock = selected_option.split(" - ")[0]

        if selected_stock != st.session_state.selected_stock:
            st.session_state.selected_stock = selected_stock
            st.rerun()

        # Pulsante aggiorna titolo selezionato
        if st.sidebar.button("🔄 Aggiorna Titolo", use_container_width=True):
            self.load_data(selected_stock, force_refresh=True)
            st.rerun()

        # Pulsante aggiorna tutti i titoli
        if st.sidebar.button("🔄 Aggiorna Tutti i Titoli", use_container_width=True, type="primary"):
            self.load_all_stocks_data(force_refresh=True)
            st.rerun()

        # Ora ultimo aggiornamento
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.session_state.last_update:
                st.info(f"📌 Titolo\n{st.session_state.last_update.strftime('%H:%M:%S')}")
        with col2:
            if st.session_state.last_full_update:
                st.success(f"📊 Tutti\n{st.session_state.last_full_update.strftime('%H:%M:%S')}")

        st.sidebar.markdown("---")

        # Auto-refresh controls
        st.sidebar.markdown("### ⏰ Auto-Refresh")

        auto_refresh = st.sidebar.toggle(
            "Abilita Auto-Refresh",
            value=st.session_state.auto_refresh_enabled,
            help="Aggiorna automaticamente i dati ogni X minuti"
        )

        if auto_refresh != st.session_state.auto_refresh_enabled:
            st.session_state.auto_refresh_enabled = auto_refresh
            if auto_refresh:
                # Reset timer quando viene abilitato
                st.session_state.next_refresh_time = datetime.now() + timedelta(
                    minutes=st.session_state.auto_refresh_interval
                )
            else:
                st.session_state.next_refresh_time = None

        if st.session_state.auto_refresh_enabled:
            refresh_interval = st.sidebar.slider(
                "Intervallo (minuti)",
                min_value=1,
                max_value=30,
                value=st.session_state.auto_refresh_interval,
                help="Frequenza di aggiornamento automatico"
            )

            if refresh_interval != st.session_state.auto_refresh_interval:
                st.session_state.auto_refresh_interval = refresh_interval
                # Aggiorna il timer con il nuovo intervallo
                st.session_state.next_refresh_time = datetime.now() + timedelta(minutes=refresh_interval)

            # Mostra prossimo aggiornamento (solo minuti approssimativi per evitare rerun continui)
            if st.session_state.next_refresh_time:
                time_remaining = (st.session_state.next_refresh_time - datetime.now()).seconds
                minutes_left = max(0, time_remaining // 60)
                if minutes_left > 0:
                    st.sidebar.success(f"⏳ Prossimo aggiornamento tra circa {minutes_left} minuti")
                else:
                    st.sidebar.success(f"⏳ Prossimo aggiornamento a breve...")
                st.sidebar.caption(f"Orario prossimo aggiornamento: {st.session_state.next_refresh_time.strftime('%H:%M')}")

        # Gestione titoli
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📋 Gestione Titoli")

        with st.sidebar.expander("➕ Aggiungi/Rimuovi Titoli", expanded=False):
            # Aggiungi titolo
            st.markdown("**Aggiungi nuovo titolo:**")
            col1, col2 = st.columns([3, 1])
            with col1:
                new_symbol = st.text_input(
                    "Simbolo (es. ENEL.MI)",
                    key="new_stock_symbol",
                    placeholder="XXX.MI"
                ).upper().strip()
            with col2:
                if st.button("➕", key="add_stock_btn"):
                    if new_symbol:
                        if new_symbol in st.session_state.active_stocks:
                            st.error("Titolo già presente!")
                        else:
                            with st.spinner(f"Validazione {new_symbol}..."):
                                if self.validate_stock_symbol(new_symbol):
                                    st.session_state.active_stocks.append(new_symbol)
                                    self.save_custom_stocks()
                                    # Reset dei dati caricati per forzare aggiornamento
                                    st.session_state.all_stocks_loaded = False
                                    st.success(f"✅ {new_symbol} aggiunto!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ Simbolo {new_symbol} non valido o non trovato")
                    else:
                        st.warning("Inserisci un simbolo")

            # Rimuovi titolo
            st.markdown("---")
            st.markdown("**Rimuovi titolo:**")
            if len(st.session_state.active_stocks) > 1:
                symbol_to_remove = st.selectbox(
                    "Seleziona titolo da rimuovere",
                    st.session_state.active_stocks,
                    key="remove_stock_select"
                )
                if st.button("🗑️ Rimuovi", key="remove_stock_btn", type="secondary"):
                    st.session_state.active_stocks.remove(symbol_to_remove)
                    self.save_custom_stocks()
                    # Reset dei dati caricati
                    st.session_state.all_stocks_loaded = False
                    if st.session_state.selected_stock == symbol_to_remove:
                        st.session_state.selected_stock = st.session_state.active_stocks[0]
                    st.success(f"✅ {symbol_to_remove} rimosso!")
                    st.rerun()
            else:
                st.info("Deve rimanere almeno un titolo nell'elenco")

            # Ripristina elenco predefinito
            st.markdown("---")
            if st.button("🔄 Ripristina Elenco Predefinito", key="reset_stocks_btn"):
                st.session_state.active_stocks = TOP_ITALIAN_STOCKS.copy()
                self.save_custom_stocks()
                st.session_state.all_stocks_loaded = False
                st.success("✅ Elenco ripristinato!")
                st.rerun()

            # Mostra numero totale di titoli monitorati
            st.markdown("---")
            st.info(f"📊 Titoli monitorati: **{len(st.session_state.active_stocks)}**")

        st.sidebar.markdown("---")
        st.sidebar.markdown("### ⚠️ Disclaimer")
        st.sidebar.warning(
            "Questo strumento fornisce previsioni basate su modelli ML e NON deve essere usato "
            "come unica base per decisioni di investimento. Fai sempre le tue ricerche."
        )

    def render_stock_info(self, symbol: str):
        """Mostra le informazioni correnti del titolo"""
        if symbol not in st.session_state.stock_data:
            return

        data = st.session_state.stock_data[symbol]
        quote = data.get('quote')

        if not quote:
            st.error("Impossibile recuperare la quotazione corrente")
            return

        # Mostra prezzo corrente
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="Prezzo Corrente",
                value=f"€{quote['current_price']:.2f}",
                delta=f"{quote['percent_change']:.2f}%"
            )

        with col2:
            st.metric(label="Massimo", value=f"€{quote['high']:.2f}")

        with col3:
            st.metric(label="Minimo", value=f"€{quote['low']:.2f}")

        with col4:
            st.metric(label="Apertura", value=f"€{quote['open']:.2f}")

    def render_sentiment(self, symbol: str):
        """Mostra l'analisi del sentiment"""
        if symbol not in st.session_state.stock_data:
            return

        data = st.session_state.stock_data[symbol]
        sentiment = data['sentiment']

        st.markdown("### 📰 Sentiment Notizie")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Punteggio Sentiment", f"{sentiment['sentiment_score']:.2f}")

        with col2:
            st.metric("Articoli Analizzati", sentiment['total_articles'])

        with col3:
            trend_color = "green" if sentiment['sentiment_score'] > 0 else "red"
            trend_text = sentiment.get('sentiment_trend', 'Neutrale')
            st.markdown(
                f"<p style='color:{trend_color}; font-size:1.2rem; font-weight:bold;'>"
                f"{trend_text}</p>",
                unsafe_allow_html=True
            )

        # Dettaglio sentiment
        col1, col2, col3 = st.columns(3)
        with col1:
            st.success(f"✅ Positivi: {sentiment['positive_count']}")
        with col2:
            st.info(f"➖ Neutrali: {sentiment['neutral_count']}")
        with col3:
            st.error(f"❌ Negativi: {sentiment['negative_count']}")

    def render_technical_signals(self, symbol: str):
        """Mostra i segnali di analisi tecnica"""
        if symbol not in st.session_state.stock_data:
            return

        data = st.session_state.stock_data[symbol]
        df = data['historical']

        signals = self.technical_analyzer.get_trading_signals(df)

        st.markdown("### 📊 Segnali Tecnici")

        for indicator, signal in signals.items():
            if 'Buy' in signal or 'BULLISH' in signal or 'Oversold' in signal:
                st.success(f"**{indicator}**: {signal}")
            elif 'Sell' in signal or 'BEARISH' in signal or 'Overbought' in signal:
                st.error(f"**{indicator}**: {signal}")
            else:
                st.info(f"**{indicator}**: {signal}")

    def render_complete_overview(self):
        """Mostra la panoramica completa di tutti i titoli"""
        st.markdown("## 🌐 Panoramica Completa - Tutti i Titoli")
        st.markdown("Andamento previsto per tutti i periodi e tutti i titoli")
        st.markdown("---")

        # Ottieni la panoramica
        df_overview = self.get_all_stocks_overview()

        # Mostra la legenda
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**↑ Rialzo** - Prezzo previsto in aumento")
        with col2:
            st.markdown("**→ Stabile** - Prezzo previsto invariato (±0.5%)")
        with col3:
            st.markdown("**↓ Ribasso** - Prezzo previsto in calo")

        st.markdown("---")

        # Funzione per applicare colori alle celle
        def color_cells(val):
            """Colora le celle in base al valore"""
            if isinstance(val, str):
                if '↑' in val or '+' in val:
                    return 'background-color: #d4edda; color: #155724'  # Verde chiaro
                elif '↓' in val or (val.startswith('-') and '%' in val):
                    return 'background-color: #f8d7da; color: #721c24'  # Rosso chiaro
            return ''

        # Applica lo styling al dataframe
        styled_df = df_overview.style.applymap(color_cells, subset=pd.IndexSlice[:, ['2 Ore', '1 Giorno', '3 Giorni', '7 Giorni']])

        # Mostra la tabella con styling
        st.dataframe(
            styled_df,
            use_container_width=True,
            height=600
        )

        # Statistiche riepilogative
        st.markdown("---")
        st.markdown("### 📊 Statistiche Riepilogative")

        periods = ['2 Ore', '1 Giorno', '3 Giorni', '7 Giorni']

        cols = st.columns(len(periods))

        for i, period in enumerate(periods):
            with cols[i]:
                st.markdown(f"**{period}**")

                # Conta trend per questo periodo
                values = df_overview[period].tolist()

                rialzo = sum(1 for v in values if isinstance(v, str) and '↑' in v)
                ribasso = sum(1 for v in values if isinstance(v, str) and '↓' in v)
                stabile = sum(1 for v in values if isinstance(v, str) and '→' in v)

                st.metric("Rialzo ↑", rialzo)
                st.metric("Ribasso ↓", ribasso)
                st.metric("Stabile →", stabile)

    def render_accuracy_analysis(self):
        """Mostra l'analisi di accuratezza delle previsioni"""
        st.markdown("## 🎯 Analisi Accuratezza Previsioni")
        st.markdown("---")

        # Ottieni statistiche generali
        overall_stats = self.prediction_logger.get_accuracy_stats()

        if overall_stats.get('evaluated_predictions', 0) == 0:
            st.info("📊 Nessuna previsione valutata disponibile ancora. "
                   "Le previsioni verranno valutate automaticamente quando raggiungeranno la loro data target.")
            st.markdown("### 📝 Cronologia Previsioni")

            # Mostra comunque le previsioni in attesa di valutazione
            history = self.prediction_logger.get_predictions_history(limit=50)
            if not history.empty:
                # Format timestamps
                history_display = history.copy()
                history_display['prediction_timestamp'] = pd.to_datetime(history_display['prediction_timestamp']).dt.strftime('%Y-%m-%d %H:%M')
                history_display['target_timestamp'] = pd.to_datetime(history_display['target_timestamp']).dt.strftime('%Y-%m-%d %H:%M')

                # Select relevant columns
                display_cols = ['prediction_timestamp', 'symbol', 'stock_name', 'horizon',
                              'current_price', 'predicted_price', 'predicted_change_pct', 'accuracy_evaluated']

                # Funzione per colorare la variazione prevista
                def color_change(val):
                    try:
                        if pd.notna(val) and isinstance(val, (int, float)):
                            if val > 0:
                                return 'background-color: #d4edda; color: #155724'
                            elif val < 0:
                                return 'background-color: #f8d7da; color: #721c24'
                    except:
                        pass
                    return ''

                # Applica styling
                styled_history = history_display[display_cols].rename(columns={
                    'prediction_timestamp': 'Data Previsione',
                    'symbol': 'Simbolo',
                    'stock_name': 'Nome',
                    'horizon': 'Orizzonte',
                    'current_price': 'Prezzo Iniziale',
                    'predicted_price': 'Prezzo Previsto',
                    'predicted_change_pct': 'Variazione Prevista %',
                    'accuracy_evaluated': 'Valutata'
                }).style.applymap(color_change, subset=['Variazione Prevista %'])

                st.dataframe(
                    styled_history,
                    use_container_width=True,
                    height=400
                )
            return

        # Statistiche globali
        st.markdown("### 📊 Statistiche Globali")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Previsioni Totali",
                overall_stats['total_predictions'],
                help="Numero totale di previsioni effettuate"
            )

        with col2:
            st.metric(
                "Previsioni Valutate",
                overall_stats['evaluated_predictions'],
                help="Previsioni per cui conosciamo il risultato reale"
            )

        with col3:
            error = overall_stats.get('average_error_pct', 0)
            st.metric(
                "Errore Medio",
                f"{error}%",
                help="Errore percentuale medio delle previsioni"
            )

        with col4:
            direction = overall_stats.get('correct_direction_pct', 0)
            st.metric(
                "Direzione Corretta",
                f"{direction}%",
                help="% di volte in cui abbiamo previsto correttamente la direzione (rialzo/ribasso)"
            )

        # Accuratezza per orizzonte temporale
        st.markdown("---")
        st.markdown("### 📈 Accuratezza per Orizzonte Temporale")

        accuracy_by_horizon = self.prediction_logger.get_accuracy_by_horizon()

        if not accuracy_by_horizon.empty:
            st.dataframe(accuracy_by_horizon, use_container_width=True)

            # Grafico accuratezza per orizzonte
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=accuracy_by_horizon['Orizzonte'],
                y=accuracy_by_horizon['Errore Medio %'],
                name='Errore Medio %',
                marker_color='lightcoral'
            ))

            fig.add_trace(go.Bar(
                x=accuracy_by_horizon['Orizzonte'],
                y=accuracy_by_horizon['Direzione Corretta %'],
                name='Direzione Corretta %',
                marker_color='lightgreen'
            ))

            fig.update_layout(
                title="Confronto Errore vs Direzione Corretta per Orizzonte",
                xaxis_title="Orizzonte Temporale",
                yaxis_title="Percentuale",
                barmode='group',
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

        # Storico previsioni recenti
        st.markdown("---")
        st.markdown("### 📝 Storico Previsioni Recenti")

        # Filtro per simbolo
        col1, col2 = st.columns([1, 3])
        with col1:
            filter_symbol = st.selectbox(
                "Filtra per simbolo",
                ["Tutti"] + self.get_active_stocks()
            )

        symbol_filter = None if filter_symbol == "Tutti" else filter_symbol

        history = self.prediction_logger.get_predictions_history(
            symbol=symbol_filter,
            limit=100
        )

        if not history.empty:
            # Format timestamps
            history_display = history.copy()
            history_display['prediction_timestamp'] = pd.to_datetime(history_display['prediction_timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            history_display['target_timestamp'] = pd.to_datetime(history_display['target_timestamp']).dt.strftime('%Y-%m-%d %H:%M')

            # Select relevant columns
            display_cols = ['prediction_timestamp', 'symbol', 'horizon', 'current_price',
                          'predicted_price', 'predicted_change_pct', 'actual_price',
                          'actual_change_pct', 'error_pct', 'accuracy_evaluated']

            # Funzione per colorare le variazioni percentuali
            def color_variation(val):
                try:
                    if pd.notna(val) and isinstance(val, (int, float)):
                        if val > 0:
                            return 'background-color: #d4edda; color: #155724; font-weight: bold'
                        elif val < 0:
                            return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
                except:
                    pass
                return ''

            # Applica styling alle colonne
            renamed_df = history_display[display_cols].rename(columns={
                'prediction_timestamp': 'Data Previsione',
                'symbol': 'Simbolo',
                'horizon': 'Orizzonte',
                'current_price': 'Prezzo Iniziale',
                'predicted_price': 'Prezzo Previsto',
                'predicted_change_pct': 'Var. Prevista %',
                'actual_price': 'Prezzo Reale',
                'actual_change_pct': 'Var. Reale %',
                'error_pct': 'Errore %',
                'accuracy_evaluated': 'Valutata'
            })

            # Applica colori alle colonne di variazione
            styled_df = renamed_df.style.applymap(
                color_variation,
                subset=['Var. Prevista %', 'Var. Reale %']
            )

            st.dataframe(
                styled_df,
                use_container_width=True,
                height=400
            )

            # Legenda colori
            st.markdown("""
            **Legenda colori:**
            - 🟢 Verde: Errore < 2% (Ottima previsione)
            - 🟡 Giallo: Errore 2-5% (Buona previsione)
            - 🔴 Rosso: Errore > 5% (Previsione da migliorare)
            - ⚪ Grigio: In attesa di valutazione
            """)

    def render_all_charts_overview(self):
        """Renderizza panoramica completa di tutti i grafici di accuratezza"""
        st.markdown("## 📊 Panoramica Completa Grafici Accuratezza")
        st.markdown("In questa pagina puoi vedere tutti i grafici di confronto tra previsioni e valori reali per tutti i titoli monitorati.")

        # Filtro orizzonte temporale
        horizon_filter = st.selectbox(
            "Seleziona orizzonte temporale",
            ["Tutti", "2h", "1d", "3d", "7d"],
            key="charts_horizon_filter"
        )

        st.markdown("---")

        # Ottieni tutti i titoli attivi
        active_stocks = self.get_active_stocks()

        # Contatore grafici mostrati
        charts_shown = 0

        # Per ogni titolo
        for symbol in active_stocks:
            stock_name = STOCK_NAMES.get(symbol, symbol)

            # Header del titolo
            st.markdown(f"### 📈 {stock_name} ({symbol})")

            # Lista orizzonti da mostrare
            horizons_to_show = []
            if horizon_filter == "Tutti":
                horizons_to_show = ["2h", "1d", "3d", "7d"]
            else:
                horizons_to_show = [horizon_filter]

            stock_has_data = False

            # Per ogni orizzonte
            for horizon in horizons_to_show:
                # Mappa nome orizzonte per visualizzazione
                horizon_names = {
                    "2h": "2 Ore",
                    "1d": "1 Giorno",
                    "3d": "3 Giorni",
                    "7d": "7 Giorni"
                }

                horizon_name = horizon_names.get(horizon, horizon)

                # Crea i grafici
                accuracy_fig = self.plot_prediction_accuracy_chart(symbol, horizon)

                if accuracy_fig:
                    stock_has_data = True

                    # Sottotitolo orizzonte
                    st.markdown(f"#### ⏱️ {horizon_name}")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.plotly_chart(accuracy_fig, use_container_width=True)

                    with col2:
                        error_fig = self.plot_prediction_error_chart(symbol, horizon)
                        if error_fig:
                            st.plotly_chart(error_fig, use_container_width=True)

                    charts_shown += 1

            if not stock_has_data:
                st.info(f"ℹ️ Non ci sono ancora dati storici per {stock_name}")

            # Separatore tra titoli
            st.markdown("---")

        # Messaggio se nessun grafico
        if charts_shown == 0:
            st.warning("⚠️ Non ci sono ancora dati storici sufficienti per visualizzare i grafici. "
                      "I grafici appariranno dopo che le previsioni saranno state valutate nel tempo.")
        else:
            st.success(f"✅ Visualizzati {charts_shown} grafici di accuratezza")

    def run(self):
        """Run the main dashboard"""
        # Sync data from GitHub (if configured)
        if 'sync_attempted' not in st.session_state:
            st.session_state.sync_attempted = False

        if not st.session_state.sync_attempted:
            with st.spinner('🔄 Sincronizzazione dati da GitHub...'):
                sync_status = get_sync_status()
                if sync_status['is_git_repo'] and sync_status['has_remote']:
                    sync_success = sync_from_github()
                    if sync_success:
                        st.success('✅ Dati sincronizzati con successo!')
                        time.sleep(1)  # Brief pause to show message
                    else:
                        st.warning('⚠️ Sincronizzazione dati non riuscita')
                st.session_state.sync_attempted = True

        # Carica titoli personalizzati se non già caricati
        if st.session_state.custom_stocks is None:
            self.load_custom_stocks()

        # Header
        st.markdown(
            f"<h1 class='main-header'>{DASHBOARD_CONFIG['title']}</h1>",
            unsafe_allow_html=True
        )

        # Sidebar
        self.render_sidebar()

        # Carica automaticamente tutti i titoli all'avvio se non già fatto
        if not st.session_state.all_stocks_loaded:
            self.load_all_stocks_data(force_refresh=False)

        # Load data for selected stock
        symbol = st.session_state.selected_stock

        # Mostra simbolo e nome completo del titolo selezionato
        stock_full_name = STOCK_NAMES.get(symbol, symbol)
        st.markdown(f"## 📊 {symbol} - {stock_full_name}")

        # Mostra ultimo aggiornamento
        if st.session_state.last_full_update:
            time_since_update = (datetime.now() - st.session_state.last_full_update).seconds // 60
            st.caption(f"📊 Ultimo aggiornamento completo: {time_since_update} minuti fa")

        st.markdown("---")

        self.load_data(symbol)

        # Display stock info
        self.render_stock_info(symbol)

        # Tab per le diverse sezioni
        tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
            ["🌐 Panoramica Completa", "📈 Titolo Selezionato", "⏱️ 2 Ore", "📅 1 Giorno", "📅 3 Giorni", "📅 7 Giorni", "🎯 Accuratezza Modello", "📊 Grafici Accuratezza"]
        )

        with tab0:
            # Panoramica completa di tutti i titoli
            self.render_complete_overview()

        with tab1:
            st.markdown("## Panoramica")

            col1, col2 = st.columns(2)

            with col1:
                self.render_sentiment(symbol)
                self.render_technical_signals(symbol)

            with col2:
                # Grafico prezzi
                fig = self.plot_price_chart(symbol)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

        # Tab previsioni
        for tab, (hours, days) in zip(
            [tab2, tab3, tab4, tab5],
            [(2, 0), (0, 1), (0, 3), (0, 7)]
        ):
            with tab:
                horizon = f"{hours} ore" if hours > 0 else f"{days} giorno" if days == 1 else f"{days} giorni"
                st.markdown(f"## Previsione {horizon}")

                # Addestra modello se non addestrato
                if not self.predictor.is_trained:
                    if self.train_model(symbol):
                        st.success("Modelli addestrati con successo!")
                    else:
                        st.error("Errore nell'addestramento dei modelli")
                        continue

                # Genera previsioni
                predictions = self.make_predictions(symbol, hours, days)

                if predictions and 'predictions' in predictions:
                    # Verifica che quote sia disponibile
                    quote = st.session_state.stock_data[symbol].get('quote')
                    if not quote:
                        st.error("❌ Impossibile recuperare i dati di quotazione correnti")
                        continue

                    # Mostra previsione
                    current_price = quote['current_price']
                    predicted_price = predictions['predictions'][-1]
                    change = ((predicted_price - current_price) / current_price) * 100

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Prezzo Corrente", f"€{current_price:.2f}")

                    with col2:
                        st.metric(
                            "Prezzo Previsto",
                            f"€{predicted_price:.2f}",
                            delta=f"{change:.2f}%"
                        )

                    with col3:
                        direction = "📈 RIALZO" if change > 0 else "📉 RIBASSO"
                        color = "green" if change > 0 else "red"
                        st.markdown(
                            f"<p style='color:{color}; font-size:2rem; font-weight:bold;'>"
                            f"{direction}</p>",
                            unsafe_allow_html=True
                        )

                    # Grafico previsione
                    fig = self.plot_prediction_chart(
                        symbol, predictions, st.session_state.stock_data[symbol]['historical']
                    )
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)

                    # Informazioni modello
                    with st.expander("📊 Informazioni Modello"):
                        st.json(predictions['model_weights'])

                else:
                    st.error("Impossibile generare previsioni")

        # Tab Accuratezza Modello
        with tab6:
            self.render_accuracy_analysis()

        # Tab Grafici Accuratezza
        with tab7:
            self.render_all_charts_overview()

        # Auto-refresh logic - controlla solo se è ora di aggiornare, senza countdown continuo
        if st.session_state.auto_refresh_enabled and st.session_state.next_refresh_time:
            if datetime.now() >= st.session_state.next_refresh_time:
                # È il momento di aggiornare TUTTI i titoli
                self.load_all_stocks_data(force_refresh=True)
                st.rerun()


if __name__ == "__main__":
    dashboard = TradingDashboard()
    dashboard.run()
