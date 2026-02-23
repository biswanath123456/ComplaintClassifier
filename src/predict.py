import os
import pickle
from dataclasses import dataclass
from typing import Optional

import sys
sys.path.insert(0, os.path.dirname(__file__))
from preprocessor import clean_text
from rules import apply_priority_rules, explain_override
from sentiment import analyze, apply_sentiment_boost

MODELS_DIR = os.path.join(os.path.dirname(__file__), "../models")


def load_model(filename):
    path = os.path.join(MODELS_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model not found: {path}. Run src/train.py first.")
    with open(path, "rb") as f:
        return pickle.load(f)


# Load once when module is imported — not on every prediction
_cat_model = load_model("category_model.pkl")
_pri_model = load_model("priority_model.pkl")


@dataclass
class Prediction:
    complaint_text:      str
    category:            str
    category_confidence: float
    priority:            str
    priority_confidence: float
    rule_override:       bool
    rule_explanation:    str
    sentiment_label:     str
    sentiment_score:     float
    sentiment_boosted:   bool


def classify(text: str) -> Prediction:
    if not text or not text.strip():
        raise ValueError("Complaint text cannot be empty.")

    clean = clean_text(text)

    # Category
    cat_probs   = _cat_model.predict_proba([clean])[0]
    cat_idx     = cat_probs.argmax()
    category    = _cat_model.classes_[cat_idx]
    cat_conf    = round(float(cat_probs[cat_idx]), 3)

    # Priority (ML)
    pri_probs   = _pri_model.predict_proba([clean])[0]
    pri_idx     = pri_probs.argmax()
    ml_priority = _pri_model.classes_[pri_idx]
    pri_conf    = round(float(pri_probs[pri_idx]), 3)

    # Rules override
    # Rules override
    final_priority, rule_triggered = apply_priority_rules(text, ml_priority)

    # Sentiment boost
    sentiment = analyze(text)
    final_priority, sentiment_boosted = apply_sentiment_boost(final_priority, sentiment)

    return Prediction(
        complaint_text      = text,
        category            = category,
        category_confidence = cat_conf,
        priority            = final_priority,
        priority_confidence = pri_conf,
        rule_override       = rule_triggered is not None,
        rule_explanation    = explain_override(rule_triggered),
        sentiment_label     = sentiment["label"],
        sentiment_score     = sentiment["compound"],
        sentiment_boosted   = sentiment_boosted,
    )


if __name__ == "__main__":
    tests = [
        "My internet has been down for 3 days and support is not responding.",
        "I was charged twice for the same subscription this month.",
        "Refund not received after 30 days.",
        "Account blocked without any notification.",
        "My package hasn't arrived, it's been 2 weeks.",
        "What are your customer support hours?",
        "I work from home and the internet has been out since yesterday.",
    ]

    for text in tests:
        p = classify(text)
        print(f"\nComplaint : {text}")
        print(f"Category  : {p.category} ({p.category_confidence:.0%})")
        print(f"Priority  : {p.priority} ({p.priority_confidence:.0%})", end="")
        print(f" ← RULE OVERRIDE" if p.rule_override else "")
        print(f"Sentiment : {p.sentiment_label} ({p.sentiment_score})", end="")
        print(f" ← BOOSTED" if p.sentiment_boosted else "")