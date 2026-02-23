import sys
sys.path.insert(0, 'src')
from sentiment import analyze, apply_sentiment_boost

complaints = [
    ("My internet is slow.", "Medium"),
    ("My internet is STILL slow after 3 weeks. This is absolutely unacceptable.", "Medium"),
    ("Charged twice and no refund after 30 days. Completely disgusting service.", "Low"),
    ("Do you have any student discounts?", "Low"),
]

for text, ml_priority in complaints:
    sentiment = analyze(text)
    final, boosted = apply_sentiment_boost(ml_priority, sentiment)
    print(f"Text     : {text[:60]}")
    print(f"Sentiment: {sentiment['label']} ({sentiment['compound']})")
    print(f"Priority : {ml_priority} -> {final} {'BOOSTED' if boosted else ''}")
    print()