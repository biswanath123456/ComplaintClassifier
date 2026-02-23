import os
import re
import pandas as pd

INPUT_PATH  = os.path.join(os.path.dirname(__file__), "../data/comcast_consumeraffairs_complaints.csv")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "../data/complaints_large.csv")

def map_priority(rating):
    if rating <= 1:
        return "High"
    elif rating <= 3:
        return "Medium"
    else:
        return "Low"

CATEGORY_PATTERNS = {
    "Billing": [
        r"bill", r"charg", r"payment", r"invoice", r"refund", r"overcharg",
        r"fee", r"price", r"cost", r"money", r"credit", r"debit", r"auto.?pay",
        r"discount", r"promo", r"overdue", r"statement", r"receipt", r"amount due",
        r"double.?charg", r"extra charg", r"hidden fee", r"rate increas",
    ],
    "Technical": [
        r"internet", r"speed", r"connect", r"outage", r"router", r"signal",
        r"wifi", r"wi-fi", r"slow", r"buffering", r"lag", r"dropout", r"modem",
        r"bandwidth", r"network", r"service interruption", r"no service",
        r"not working", r"goes down", r"keeps disconnect", r"cable box",
        r"channel", r"stream", r"on demand", r"xfinity app", r"equipment",
    ],
    "Delivery": [
        r"install", r"technician", r"appointment", r"setup", r"visit",
        r"no.show", r"reschedul", r"dispatch", r"arrival", r"missed appointment",
        r"never showed", r"didn.t show", r"service call", r"truck", r"field",
    ],
    "Account": [
        r"account", r"login", r"password", r"profile", r"access", r"username",
        r"email", r"cancel", r"subscription", r"plan", r"upgrade", r"downgrade",
        r"portal", r"online account", r"my account", r"locked out", r"reset",
        r"contract", r"agreement", r"terms",
    ],
}

def map_category(text):
    if not isinstance(text, str):
        return "Other"
    text_lower = text.lower()

    scores = {}
    for category, patterns in CATEGORY_PATTERNS.items():
        count = sum(len(re.findall(p, text_lower)) for p in patterns)
        scores[category] = count

    best_category = max(scores, key=scores.get)
    best_score    = scores[best_category]

    if best_score == 0:
        return "Other"

    return best_category

def main():
    print("Loading dataset...")
    df = pd.read_csv(INPUT_PATH)
    print(f"Loaded {len(df)} rows")

    df = df.dropna(subset=["text"])
    print(f"After dropping nulls: {len(df)} rows")

    df = df.dropna(subset=["rating"])
    df = df[["text", "rating"]].copy()
    df.columns = ["complaint_text", "rating"]

    df["complaint_text"] = df["complaint_text"].str.slice(0, 1000)
    df = df[df["complaint_text"].str.len() >= 30]

    # Step 1 — label priority
    print("Labeling priority...")
    df["priority"] = df["rating"].astype(int).apply(map_priority)

    # Step 2 — label category
    print("Labeling category...")
    df["category"] = df["complaint_text"].apply(map_category)

    # Step 3 — rebalance priority
    print("Rebalancing priority distribution...")
    high   = df[df["priority"] == "High"].sample(n=1500, random_state=42)
    medium = df[df["priority"] == "Medium"]
    low    = df[df["priority"] == "Low"]
    df     = pd.concat([high, medium, low], ignore_index=True)
    print(f"After priority rebalancing: {len(df)} rows")

    # Step 4 — rebalance category
    print("Rebalancing category distribution...")
    target = 300
    balanced_cats = []
    for cat in ["Billing", "Technical", "Other", "Delivery", "Account"]:
        cat_df = df[df["category"] == cat]
        if len(cat_df) >= target:
            balanced_cats.append(cat_df.sample(n=target, random_state=42))
        else:
            balanced_cats.append(cat_df)
    df = pd.concat(balanced_cats, ignore_index=True)
    print(f"After category rebalancing: {len(df)} rows")

    # Final
    df = df[["complaint_text", "category", "priority"]]

    print(f"\nFinal rows: {len(df)}")
    print(f"\nCategory distribution:\n{df['category'].value_counts()}")
    print(f"\nPriority distribution:\n{df['priority'].value_counts()}")

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved -> {OUTPUT_PATH}")

if __name__ == "__main__":
    main()