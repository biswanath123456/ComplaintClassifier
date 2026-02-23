import urllib.request
import json

url = "http://localhost:5000/feedback"
payload = {
    "complaint_id"       : 3,
    "complaint_text"     : "My package arrived damaged.",
    "predicted_category" : "Delivery",
    "predicted_priority" : "High",
    "correct_category"   : "Delivery",
    "correct_priority"   : "Medium"
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as response:
    print(json.loads(response.read()))