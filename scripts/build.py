import sys
import json
import csv
import os
import glob

TRANSLATIONS_DIR = "translations"

def build(lang_code):
    lang_path = os.path.join(TRANSLATIONS_DIR, lang_code)
    if not os.path.exists(lang_path):
        print(f"Error: Translation directory not found at {lang_path}")
        sys.exit(1)

    # Find all .ro files in the language directory
    ro_files = glob.glob(os.path.join(lang_path, "*.ro"))
    if not ro_files:
        print(f"No .ro files found in {lang_path}")
        return

    all_data = {}
    for ro_file in ro_files:
        try:
            with open(ro_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_data.update(data)
        except Exception as e:
            print(f"Error reading {ro_file}: {e}")

    # Filter keys with non-empty values
    rows = []
    for k, v in all_data.items():
        if v and v.strip():
            rows.append([k, v])

    if not rows:
        print(f"No translations found in {lang_path}")
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
