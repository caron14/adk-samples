from adk.tools import tool
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Ensure VADER lexicon is downloaded
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except nltk.downloader.DownloadError:
    print("NLTK VADER lexicon not found. Downloading...")
    nltk.download('vader_lexicon', quiet=True)
except LookupError: # Fallback for environments where find might behave differently
   try:
       SentimentIntensityAnalyzer() # Instantiation might trigger download or confirm availability
   except LookupError as e: # Check specific error for vader_lexicon
       if "vader_lexicon" in str(e):
           print("NLTK VADER lexicon not found on LookupError. Downloading...")
           nltk.download('vader_lexicon', quiet=True)
       else:
           raise e # Re-raise if it's a different lookup error


@tool
def analyze_sentiment(text: str) -> dict:
    """
    Analyzes the sentiment of a given text using NLTK's VADER.
    Returns a dictionary with sentiment scores (negative, neutral, positive, compound).
    The compound score ranges from -1 (most extreme negative) to +1 (most extreme positive).
    """
    if not text or not isinstance(text, str):
        return {"error": "Input text must be a non-empty string."}

    try:
        analyzer = SentimentIntensityAnalyzer()
        sentiment_scores = analyzer.polarity_scores(text)
        return sentiment_scores
    except Exception as e:
        return {"error": f"Error during sentiment analysis: {str(e)}"}
