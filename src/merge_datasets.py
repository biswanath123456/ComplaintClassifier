import os
import pandas as pd

ORIGINAL_PATH = os.path.join(os.path.dirname(__file__), "../data/complaints.csv")
LARGE_PATH    = os.path.join(os.path.dirname(__file__), "../data/complaints_large.csv")
OUTPUT_PATH   = os.path.join(os.path.dirname(__file__), "../data/complaints_final.csv")

def main():
    original = pd.read_csv(ORIGINAL_PATH)
    large    = pd.read_csv(LARGE_PATH)

    original["source"] = "manual"
    large["source"]    = "comcast"

    combined = pd.concat([original, large], ignore_index=True)
    combined = combined[["complaint_text", "category", "priority"]]
    combined = combined.dropna()
    combined = combined.drop_duplicates(subset=["complaint_text"])

    print(f"Original rows : {len(original)}")
    print(f"Comcast rows  : {len(large)}")
    print(f"Combined rows : {len(combined)}")
    print(f"\nCategory distribution:\n{combined['category'].value_counts()}")
    print(f"\nPriority distribution:\n{combined['priority'].value_counts()}")

    combined.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved -> {OUTPUT_PATH}")

if __name__ == "__main__":
    main()