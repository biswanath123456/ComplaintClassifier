from nltk.sentiment.vader import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()

# Threshold below which we consider sentiment upgrade-worthy
NEGATIVE_THRESHOLD = -0.5


def analyze(text: str) -> dict:
    scores = _analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound <= -0.6:
        label = "Very Negative"
    elif compound <= -0.2:
        label = "Negative"
    elif compound <= 0.2:
        label = "Neutral"
    else:
        label = "Positive"

    return {
        "compound": round(compound, 3),
        "label": label,
        "should_boost": compound <= NEGATIVE_THRESHOLD,
    }


def apply_sentiment_boost(priority: str, sentiment: dict) -> tuple[str, bool]:
    """
    Upgrades priority one level if sentiment is very negative.
    High stays High — already at maximum.
    Medium → High
    Low → Medium
    """
    if not sentiment["should_boost"]:
        return priority, False

    if priority == "Medium":
        return "High", True
    elif priority == "Low":
        return "Medium", True

    return priority, False