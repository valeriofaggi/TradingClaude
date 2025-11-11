"""
Sentiment Analysis Module
Analyze financial news sentiment to support trading predictions
"""

from typing import List, Dict
import logging
from textblob import TextBlob
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyze sentiment of financial news"""

    def __init__(self):
        """Initialize sentiment analyzer"""
        self.financial_keywords = {
            'positive': [
                'profit', 'growth', 'increase', 'gain', 'rise', 'up', 'high',
                'strong', 'beat', 'exceed', 'success', 'improve', 'surge',
                'rally', 'bullish', 'outperform', 'upgrade', 'buy'
            ],
            'negative': [
                'loss', 'decline', 'decrease', 'drop', 'fall', 'down', 'low',
                'weak', 'miss', 'fail', 'concern', 'risk', 'crash', 'plunge',
                'bearish', 'underperform', 'downgrade', 'sell', 'warning'
            ]
        }

    def analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of a single text

        Args:
            text: Text to analyze

        Returns:
            Dictionary with sentiment scores
        """
        if not text:
            return {'polarity': 0.0, 'subjectivity': 0.0, 'classification': 'neutral'}

        # Use TextBlob for basic sentiment
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        # Enhance with financial keywords
        text_lower = text.lower()
        pos_count = sum(1 for word in self.financial_keywords['positive'] if word in text_lower)
        neg_count = sum(1 for word in self.financial_keywords['negative'] if word in text_lower)

        # Adjust polarity based on financial keywords
        if pos_count > 0 or neg_count > 0:
            keyword_sentiment = (pos_count - neg_count) / (pos_count + neg_count)
            polarity = (polarity + keyword_sentiment) / 2

        # Classify sentiment
        if polarity > 0.1:
            classification = 'positive'
        elif polarity < -0.1:
            classification = 'negative'
        else:
            classification = 'neutral'

        return {
            'polarity': round(polarity, 3),
            'subjectivity': round(subjectivity, 3),
            'classification': classification,
            'positive_keywords': pos_count,
            'negative_keywords': neg_count
        }

    def analyze_news_list(self, news_articles: List[Dict]) -> Dict:
        """
        Analyze sentiment of multiple news articles

        Args:
            news_articles: List of news article dictionaries

        Returns:
            Aggregated sentiment analysis
        """
        if not news_articles:
            return {
                'avg_sentiment': 0.0,
                'sentiment_score': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_articles': 0,
                'sentiment_trend': 'No Data'
            }

        sentiments = []
        classifications = {'positive': 0, 'negative': 0, 'neutral': 0}

        for article in news_articles:
            # Combine headline and summary for analysis
            text = f"{article.get('headline', '')} {article.get('summary', '')}"
            sentiment = self.analyze_text(text)

            sentiments.append(sentiment['polarity'])
            classifications[sentiment['classification']] += 1

        # Calculate aggregated metrics
        avg_sentiment = np.mean(sentiments) if sentiments else 0.0

        # Weighted sentiment score (-1 to 1)
        total = len(news_articles)
        sentiment_score = (
            (classifications['positive'] - classifications['negative']) / total
            if total > 0 else 0.0
        )

        return {
            'avg_sentiment': round(avg_sentiment, 3),
            'sentiment_score': round(sentiment_score, 3),
            'positive_count': classifications['positive'],
            'negative_count': classifications['negative'],
            'neutral_count': classifications['neutral'],
            'total_articles': total,
            'sentiment_trend': self._get_sentiment_trend(sentiment_score)
        }

    def _get_sentiment_trend(self, score: float) -> str:
        """Convert sentiment score to trend description"""
        if score > 0.3:
            return 'Very Positive'
        elif score > 0.1:
            return 'Positive'
        elif score < -0.3:
            return 'Very Negative'
        elif score < -0.1:
            return 'Negative'
        else:
            return 'Neutral'

    def get_sentiment_weight(self, news_sentiment: Dict, default_weight: float = 0.3) -> float:
        """
        Calculate sentiment weight for prediction model

        Args:
            news_sentiment: Sentiment analysis results
            default_weight: Default weight if no sentiment

        Returns:
            Weight value between -1 and 1
        """
        if not news_sentiment or news_sentiment['total_articles'] == 0:
            return 0.0

        # Scale sentiment score by number of articles (more articles = more confidence)
        article_count = news_sentiment['total_articles']
        confidence_multiplier = min(article_count / 20, 1.0)  # Cap at 20 articles

        return news_sentiment['sentiment_score'] * confidence_multiplier * default_weight


if __name__ == "__main__":
    # Test sentiment analyzer
    analyzer = SentimentAnalyzer()

    # Test samples
    test_news = [
        {
            'headline': 'Company reports record profits and strong growth',
            'summary': 'The company exceeded expectations with a 25% increase in revenue.'
        },
        {
            'headline': 'Stock plunges amid concerns over market conditions',
            'summary': 'Investors worried about potential losses in the coming quarter.'
        },
        {
            'headline': 'Company announces new product line',
            'summary': 'The firm is expanding into new markets.'
        }
    ]

    # Analyze each article
    print("Individual Article Sentiment:")
    for article in test_news:
        text = f"{article['headline']} {article['summary']}"
        sentiment = analyzer.analyze_text(text)
        print(f"\nHeadline: {article['headline']}")
        print(f"Sentiment: {sentiment}")

    # Aggregate analysis
    print("\n" + "="*50)
    print("Aggregated Sentiment Analysis:")
    aggregate = analyzer.analyze_news_list(test_news)
    for key, value in aggregate.items():
        print(f"{key}: {value}")
