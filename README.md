# Complaint Classifier

An end-to-end NLP system that automatically classifies customer complaints by category and priority. Built to simulate a real enterprise support system used by banks, telecoms, and e-commerce companies.

## What it does

Takes a raw customer complaint as input and returns:
- **Category** — Billing, Technical, Delivery, Account, or Other
- **Priority** — High, Medium, or Low

Priority is determined by three independent layers:
1. ML model prediction
2. Rule-based override for critical patterns like "refund not received" or "account blocked"
3. Sentiment boost if the complaint tone is very negative

Every prediction is stored in a database. Support agents can submit corrections through a feedback endpoint, and the model retrains on those corrections automatically.

## Tech Stack

- Python
- Scikit-learn — TF-IDF + Logistic Regression
- NLTK — text cleaning and VADER sentiment analysis
- Flask — REST API and analytics dashboard
- SQLite — complaint and feedback persistence

## Project Structure
```
complaint-classifier/
├── data/complaints.csv        # Training data
├── database/db.py             # Database layer
├── src/preprocessor.py        # Text cleaning
├── src/rules.py               # Rule engine
├── src/sentiment.py           # Sentiment analysis
├── src/train.py               # Model training
├── src/predict.py             # Inference pipeline
├── src/retrain.py             # Feedback-aware retraining
├── api/app.py                 # REST API
└── dashboard/app.py           # Analytics dashboard
```

## Setup
```bash
git clone https://github.com/yourusername/complaint-classifier.git
cd complaint-classifier
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt'); nltk.download('vader_lexicon')"
```

## Usage

**Train the model**
```bash
python src/train.py
```

**Start the API**
```bash
python api/app.py
```

**Classify a complaint**
```bash
curl -X POST http://localhost:5000/classify-complaint \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"My internet has been down for 3 days and nobody is responding.\"}"
```

**Submit agent feedback**
```bash
curl -X POST http://localhost:5000/feedback \
  -H "Content-Type: application/json" \
  -d "{\"complaint_id\": 1, \"complaint_text\": \"...\", \"predicted_category\": \"Technical\", \"predicted_priority\": \"Medium\", \"correct_category\": \"Technical\", \"correct_priority\": \"High\"}"
```

**Retrain on feedback**
```bash
python src/retrain.py
```

**View dashboard**
```bash
python dashboard/app.py
# Open http://localhost:5001
```

## API Response
```json
{
  "complaint_text": "My internet has been down for 3 days.",
  "category": "Technical",
  "category_confidence": 0.412,
  "priority": "High",
  "priority_confidence": 0.506,
  "rule_override": true,
  "rule_explanation": "Priority overridden to High — rule matched.",
  "sentiment_label": "Negative",
  "sentiment_score": -0.509,
  "sentiment_boosted": false,
  "classified_at": "2026-02-23T10:00:00"
}
```

## Key Design Decisions

**Two models instead of one** — category and priority are trained separately. Easier to debug, easier to retrain independently, cleaner failure modes.

**Rule engine on top of ML** — companies do not trust pure ML blindly. Critical complaints like account hacks or payment failures are too important to leave to a probabilistic model.

**Sentiment as a third layer** — two complaints with identical words but different tone should not get the same priority. VADER catches the emotional urgency that TF-IDF misses.

**Feedback loop** — agent corrections are stored and used to retrain. The model improves from real usage without manual data labeling.