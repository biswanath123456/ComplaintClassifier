import urllib.request
import json

complaints = [
    "I have been charged three times this month and nobody is picking up the phone.",
    "My internet has been completely dead for 4 days. I work from home and I am losing money.",
    "The technician was supposed to come yesterday and never showed up.",
    "I cannot log into my account. It says my password is wrong but I just reset it.",
    "Do you offer any student discounts on your plans?",
    "Refund not received after 45 days. I was promised it within a week.",
    "My cable box is showing a blank screen since this morning.",
    "Someone changed my account email and I cannot get back in.",
    "The router keeps dropping connection every 30 minutes.",
    "I was billed for a premium package I never subscribed to.",
]

url = "http://localhost:5000/classify-complaint"

for text in complaints:
    payload = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
        print(f"Complaint : {text[:70]}...")
        print(f"Category  : {result['category']} ({result['category_confidence']:.0%})")
        print(f"Priority  : {result['priority']} ({result['priority_confidence']:.0%})", end="")
        print(" <- RULE OVERRIDE" if result['rule_override'] else "", end="")
        print(" <- SENTIMENT BOOST" if result['sentiment_boosted'] else "")
        print(f"Sentiment : {result['sentiment_label']} ({result['sentiment_score']})")
        print()