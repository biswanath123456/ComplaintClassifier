import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../database"))

from flask import Flask, render_template_string
from db import get_all_complaints, get_category_counts, get_priority_counts, get_high_priority_trend

app = Flask(__name__)

# Simple HTML template for the dashboard
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Complaint Classifier Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        h1 { color: #333; }
        h2 { color: #555; margin-top: 40px; }
        .cards { display: flex; gap: 20px; margin-bottom: 30px; }
        .card {
            background: white; padding: 20px 30px; border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1); min-width: 150px;
        }
        .card h3 { margin: 0; font-size: 2em; color: #2c7be5; }
        .card p { margin: 5px 0 0; color: #888; }
        table {
            width: 100%; border-collapse: collapse;
            background: white; border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        th { background: #2c7be5; color: white; padding: 12px 16px; text-align: left; }
        td { padding: 10px 16px; border-bottom: 1px solid #eee; }
        tr:last-child td { border-bottom: none; }
        .High { color: #e63946; font-weight: bold; }
        .Medium { color: #f4a261; font-weight: bold; }
        .Low { color: #2a9d8f; font-weight: bold; }
        .badge {
            padding: 2px 10px; border-radius: 12px;
            font-size: 0.85em; font-weight: bold;
        }
        .rule-yes { background: #ffe0e0; color: #c0392b; }
        .rule-no  { background: #e0f0e0; color: #27ae60; }
    </style>
</head>
<body>
    <h1>Complaint Classifier Dashboard</h1>

    <!-- Summary Cards -->
    <div class="cards">
        <div class="card">
            <h3>{{ total }}</h3>
            <p>Total Complaints</p>
        </div>
        {% for priority, count in priority_counts %}
        <div class="card">
            <h3 class="{{ priority }}">{{ count }}</h3>
            <p>{{ priority }} Priority</p>
        </div>
        {% endfor %}
    </div>

    <!-- Category Breakdown -->
    <h2>Complaints by Category</h2>
    <table>
        <tr><th>Category</th><th>Count</th></tr>
        {% for category, count in category_counts %}
        <tr><td>{{ category }}</td><td>{{ count }}</td></tr>
        {% endfor %}
    </table>

    <!-- High Priority Trend -->
    <h2>High Priority Trend</h2>
    <table>
        <tr><th>Date</th><th>High Priority Count</th></tr>
        {% for day, count in trend %}
        <tr><td>{{ day }}</td><td>{{ count }}</td></tr>
        {% endfor %}
    </table>

    <!-- Recent Complaints -->
    <h2>Recent Complaints</h2>
    <table>
        <tr>
            <th>#</th>
            <th>Complaint</th>
            <th>Category</th>
            <th>Priority</th>
            <th>Rule Override</th>
            <th>Time</th>
        </tr>
        {% for row in complaints %}
        <tr>
            <td>{{ row[0] }}</td>
            <td>{{ row[1][:80] }}{% if row[1]|length > 80 %}...{% endif %}</td>
            <td>{{ row[2] }}</td>
            <td class="{{ row[3] }}">{{ row[3] }}</td>
            <td>
                {% if row[4] %}
                <span class="badge rule-yes">Yes</span>
                {% else %}
                <span class="badge rule-no">No</span>
                {% endif %}
            </td>
            <td>{{ row[5][:19] }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# Dashboard route
@app.route("/")
def dashboard():
    complaints      = get_all_complaints()
    category_counts = get_category_counts()
    priority_counts = get_priority_counts()
    trend           = get_high_priority_trend()
    total           = len(complaints)

    return render_template_string(
        HTML,
        complaints      = complaints,
        category_counts = category_counts,
        priority_counts = priority_counts,
        trend           = trend,
        total           = total,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)