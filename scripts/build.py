import sys
import json
import csv
import os

TRANSLATIONS_DIR = "translations"

def build(lang_code):
    json_path = os.path.join(TRANSLATIONS_DIR, f"{lang_code}.json")
    if not os.path.exists(json_path):
        print(f"Error: Translation file not found at {json_path}")
        sys.exit(1)

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {json_path}: {e}")
        sys.exit(1)

    # Filter keys with non-empty values
    rows = []
    for k, v in data.items():
        if v and v.strip():
            rows.append([k, v])

    if not rows:
        print(f"No translations found in {json_path}")
        return

    csv_path = f"{lang_code}.csv"
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["English", "Translation"])
            writer.writerows(rows)
        print(f"Exported {len(rows)} translations to {csv_path}")
    except Exception as e:
        print(f"Error writing CSV: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/build.py <lang_code>")
        sys.exit(1)

    lang_code = sys.argv[1]
    build(lang_code)
