import os
import pickle
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report

import sys
sys.path.insert(0, os.path.dirname(__file__))
from preprocessor import clean_text

DATA_PATH  = os.path.join(os.path.dirname(__file__), "../data/complaints.csv")  #Path to the dataset CSV file
MODELS_DIR = os.path.join(os.path.dirname(__file__), "../models")   #Directory to save trained models
SEED       = 42             #Random seed for reproducibility


# Ensure the models directory exists
os.makedirs(MODELS_DIR, exist_ok=True)

# Load and preprocess the dataset
def load_data():
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()
    df["complaint_text"] = df["complaint_text"].astype(str).str.strip()
    df["category"]       = df["category"].str.strip()
    df["priority"]       = df["priority"].str.strip()
    print(f"Loaded {len(df)} records\n")
    print(df["category"].value_counts(), "\n")
    print(df["priority"].value_counts(), "\n")
    return df

# Build a machine learning pipeline for text classification
def build_pipeline():
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
            min_df=1,
        )), #Convert text to TF-IDF features
        ("clf", LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=SEED,
        ))  #Train a logistic regression classifier with balanced class weights
    ])
# Why Logistic Regression? 
# It's a strong baseline for text classification tasks, especially with TF-IDF features. 
# It handles high-dimensional data well and provides interpretable coefficients, which can help identify important words or phrases influencing the predictions.


# Evaluate the model and print classification metrics
def evaluate(model, X_test, y_test, label):
    print(f"\n{'='*50}")
    print(f"  {label}")
    print(f"{'='*50}")
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred, zero_division=0))

# Save the trained model to disk using pickle
def save_model(model, filename):
    path = os.path.join(MODELS_DIR, filename)
    with open(path, "wb") as f:
        pickle.dump(model, f)
    print(f"Saved -> {path}")


# Main function to orchestrate data loading, preprocessing, model training, evaluation, and saving.
def main():
    df = load_data()

    print("Cleaning text...")
    df["clean_text"] = df["complaint_text"].apply(clean_text)

    # Prepare features and labels for both category and priority classification
    X    = df["clean_text"]
    y_cat = df["category"]
    y_pri = df["priority"]

    # Split the dataset into training and testing sets with stratification to maintain class distribution
    X_train, X_test, yc_train, yc_test, yp_train, yp_test = train_test_split(
        X, y_cat, y_pri,
        test_size=0.2,
        random_state=SEED,
        stratify=y_cat,
    )

    # Print the number of training and testing samples for verification
    print(f"Train: {len(X_train)} | Test: {len(X_test)}\n")

    # Train and evaluate the category classification model
    print("Training Category model...")
    cat_model = build_pipeline()
    cat_model.fit(X_train, yc_train)
    evaluate(cat_model, X_test, yc_test, "CATEGORY")
    save_model(cat_model, "category_model.pkl")

    # Train and evaluate the priority classification model
    print("\nTraining Priority model...")
    pri_model = build_pipeline()
    pri_model.fit(X_train, yp_train)
    evaluate(pri_model, X_test, yp_test, "PRIORITY")
    save_model(pri_model, "priority_model.pkl")

    print("\nDone. Both models saved.")


if __name__ == "__main__":
    main()