import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))
# Add database path for imports
from flask import Flask, request, jsonify
from datetime import datetime
from predict import classify
# Add database path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../database"))
from db import save_complaint, save_feedback, get_feedback_accuracy
app = Flask(__name__)

# Health check route
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    })

# Classification route
@app.route("/classify-complaint", methods=["POST"])
def classify_complaint():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400
    # Validate input
    data = request.get_json()
    text = data.get("text", "").strip()
    # Basic input validation
    if not text:
        return jsonify({"error": "Field 'text' is required and cannot be empty."}), 400
    # Limit input length to prevent abuse
    if len(text) > 2000:
        return jsonify({"error": "Text exceeds maximum length of 2000 characters."}), 400
    # Perform classification
    try:
        pred = classify(text)
    except Exception as e:
        return jsonify({"error": "Classification failed. Please try again."}), 500
    
    # Save to database
    save_complaint(pred.complaint_text, pred.category, pred.priority, pred.rule_override)
    return jsonify({
        "complaint_text":       pred.complaint_text,
        "category":             pred.category,
        "category_confidence":  pred.category_confidence,
        "priority":             pred.priority,
        "priority_confidence":  pred.priority_confidence,
        "rule_override":        pred.rule_override,
        "rule_explanation":     pred.rule_explanation,
        "classified_at":        datetime.utcnow().isoformat(),
        "sentiment_label":     pred.sentiment_label,
        "sentiment_score":     pred.sentiment_score,
        "sentiment_boosted":   pred.sentiment_boosted,
    }), 200


@app.route("/feedback", methods=["POST"])
def feedback():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()

    required = ["complaint_id", "complaint_text", "predicted_category",
                "predicted_priority", "correct_category", "correct_priority"]

    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    valid_categories = {"Billing", "Technical", "Delivery", "Account", "Other"}
    valid_priorities = {"High", "Medium", "Low"}

    if data["correct_category"] not in valid_categories:
        return jsonify({"error": f"Invalid category. Choose from {valid_categories}"}), 400

    if data["correct_priority"] not in valid_priorities:
        return jsonify({"error": f"Invalid priority. Choose from {valid_priorities}"}), 400

    try:
        save_feedback(
            complaint_id        = data["complaint_id"],
            complaint_text      = data["complaint_text"],
            predicted_category  = data["predicted_category"],
            predicted_priority  = data["predicted_priority"],
            correct_category    = data["correct_category"],
            correct_priority    = data["correct_priority"],
        )
        accuracy = get_feedback_accuracy()
    except Exception as e:
        return jsonify({"error": "Failed to save feedback."}), 500

    return jsonify({
        "message"         : "Feedback saved successfully.",
        "is_correct"      : data["predicted_category"] == data["correct_category"] and
                            data["predicted_priority"] == data["correct_priority"],
        "overall_accuracy": accuracy,
        "submitted_at"    : datetime.utcnow().isoformat(),
    }), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)