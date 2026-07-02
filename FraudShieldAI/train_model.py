"""
train_model.py
----------------
Trains the FraudShield AI ML pipeline:

1. TF-IDF vectorizer (shared) on all messages.
2. Logistic Regression classifier -> predicts label: "Scam" / "Safe"
3. Logistic Regression classifier -> predicts fraud_type (trained only on Scam rows)

Artifacts saved to /model:
    vectorizer.pkl
    label_model.pkl
    type_model.pkl

Run:
    python train_model.py
"""

import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

DATA_PATH = "data/dataset.csv"
MODEL_DIR = "model"

def main():
    df = pd.read_csv(DATA_PATH)
    df.dropna(subset=["message", "label"], inplace=True)

    # -------- Shared TF-IDF vectorizer -------- #
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        max_features=5000,
    )
    X_all = vectorizer.fit_transform(df["message"])

    # -------- Model 1: Scam vs Safe -------- #
    y_label = df["label"]
    X_train, X_test, y_train, y_test = train_test_split(
        X_all, y_label, test_size=0.2, random_state=42, stratify=y_label
    )
    label_model = LogisticRegression(max_iter=1000, class_weight="balanced")
    label_model.fit(X_train, y_train)
    preds = label_model.predict(X_test)
    print("=== Scam/Safe Classifier ===")
    print("Accuracy:", accuracy_score(y_test, preds))
    print(classification_report(y_test, preds))

    # -------- Model 2: Fraud type (Scam rows only) -------- #
    scam_df = df[df["label"] == "Scam"]
    X_scam = vectorizer.transform(scam_df["message"])
    y_type = scam_df["fraud_type"]

    Xt_train, Xt_test, yt_train, yt_test = train_test_split(
        X_scam, y_type, test_size=0.2, random_state=42, stratify=y_type
    )
    type_model = LogisticRegression(max_iter=1000, class_weight="balanced")
    type_model.fit(Xt_train, yt_train)
    preds_type = type_model.predict(Xt_test)
    print("\n=== Fraud Type Classifier ===")
    print("Accuracy:", accuracy_score(yt_test, preds_type))
    print(classification_report(yt_test, preds_type))

    # -------- Save artifacts -------- #
    joblib.dump(vectorizer, f"{MODEL_DIR}/vectorizer.pkl")
    joblib.dump(label_model, f"{MODEL_DIR}/label_model.pkl")
    joblib.dump(type_model, f"{MODEL_DIR}/type_model.pkl")
    print(f"\nSaved vectorizer.pkl, label_model.pkl, type_model.pkl to /{MODEL_DIR}")

if __name__ == "__main__":
    main()