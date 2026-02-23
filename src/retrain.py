import os
import sys
import pickle
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../database"))

from preprocessor import clean_text
from db import get_all_feedback

DATA_PATH  = os.path.join(os.path.dirname(__file__), "../data/complaints.csv")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "../models")
SEED       = 42


def load_original_data():
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()
    df = df[["complaint_text", "category", "priority"]]
    df["source"] = "original"
    return df


def load_feedback_data():
    rows = get_all_feedback()
    if not rows:
        return pd.DataFrame()

    records = []
    for row in rows:
        # row = (id, complaint_id, complaint_text, predicted_cat,
        #        predicted_pri, correct_cat, correct_pri, is_correct, submitted_at)
        records.append({
            "complaint_text": row[2],
            "category"      : row[5],  # correct_category
            "priority"      : row[6],  # correct_priority
            "source"        : "feedback"
        })

    return pd.DataFrame(records)


def build_pipeline():
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
            min_df=1,
        )),
        ("clf", LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=SEED,
        ))
    ])


def save_model(model, filename):
    path = os.path.join(MODELS_DIR, filename)
    with open(path, "wb") as f:
        pickle.dump(model, f)
    print(f"Saved -> {path}")


def main():
    print("Loading original training data...")
    original = load_original_data()
    print(f"Original rows: {len(original)}")

    print("Loading feedback data...")
    feedback = load_feedback_data()

    if feedback.empty:
        print("No feedback found. Using original data only.")
        df = original
    else:
        print(f"Feedback rows: {len(feedback)}")
        df = pd.concat([original, feedback], ignore_index=True)
        print(f"Combined rows: {len(df)}")
        print(f"\nFeedback sources:\n{df['source'].value_counts()}")

    print("\nCleaning text...")
    df["clean_text"] = df["complaint_text"].apply(clean_text)

    X     = df["clean_text"]
    y_cat = df["category"]
    y_pri = df["priority"]

    X_train, X_test, yc_train, yc_test, yp_train, yp_test = train_test_split(
        X, y_cat, y_pri,
        test_size=0.2,
        random_state=SEED,
        stratify=y_cat,
    )

    print(f"\nTrain: {len(X_train)} | Test: {len(X_test)}")

    print("\nRetraining Category model...")
    cat_model = build_pipeline()
    cat_model.fit(X_train, yc_train)
    print(classification_report(cat_model.predict(X_test), yc_test, zero_division=0))
    save_model(cat_model, "category_model.pkl")

    print("\nRetraining Priority model...")
    pri_model = build_pipeline()
    pri_model.fit(X_train, yp_train)
    print(classification_report(pri_model.predict(X_test), yp_test, zero_division=0))
    save_model(pri_model, "priority_model.pkl")

    print("\nRetrain complete. Models updated.")


if __name__ == "__main__":
    main()