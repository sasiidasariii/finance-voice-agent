from textblob import TextBlob

def compute_asia_tech_exposure(portfolio):
    total = sum(portfolio.values())
    asia_tech = sum(v for k, v in portfolio.items() if "AsiaTech" in k)
    return round((asia_tech / total) * 100, 2)

# Add sentiment analysis function
def get_sentiment(text):
    """
    Analyzes sentiment of the given text and returns a sentiment label and reason.
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0.1:
        return {"label": "positive", "reason": "positive news sentiment"}
    elif polarity < -0.1:
        return {"label": "negative", "reason": "negative news sentiment"}
    else:
        return {"label": "neutral", "reason": "mixed or minimal news sentiment"}
