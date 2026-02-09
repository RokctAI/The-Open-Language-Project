import os
import glob
import json
import requests
import polib

# Configuration
SOURCES = [
    "https://raw.githubusercontent.com/frappe/frappe/develop/frappe/locale/main.pot",
    "https://raw.githubusercontent.com/frappe/erpnext/develop/erpnext/locale/main.pot",
    "https://raw.githubusercontent.com/django/django/main/django/conf/locale/en/LC_MESSAGES/django.po",
    "https://raw.githubusercontent.com/GNOME/glib/main/po/en_GB.po"
]

TRANSLATIONS_DIR = "translations"
UPSTREAM_CACHE_DIR = ".upstream_cache"

def ensure_dirs():
    if not os.path.exists(UPSTREAM_CACHE_DIR):
        os.makedirs(UPSTREAM_CACHE_DIR)
    if not os.path.exists(TRANSLATIONS_DIR):
        os.makedirs(TRANSLATIONS_DIR)

def harvest():
    ensure_dirs()
    all_msgids = set()

    # 1. Collect unique keys from all sources
    for url in SOURCES:
        try:
            print(f"Fetching {url}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Save temporarily for polib
            filename = os.path.join(UPSTREAM_CACHE_DIR, "temp.po")
            with open(filename, "wb") as f:
                f.write(response.content)

            po = polib.pofile(filename)
            count = 0
            for entry in po:
                if entry.msgid:
                    all_msgids.add(entry.msgid)
                    count += 1
            print(f"  Found {count} keys.")

        except Exception as e:
            print(f"Error processing {url}: {e}")

    print(f"Total unique keys collected: {len(all_msgids)}")

    # 2. Update translation files
    json_files = glob.glob(os.path.join(TRANSLATIONS_DIR, "*.json"))

    for json_file in json_files:
        print(f"Updating {json_file}...")
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        modified = False
        for msgid in all_msgids:
            if msgid not in data:
                data[msgid] = ""
                modified = True

        if modified:
            # Sort keys for consistency (optional but good for git diffs)
            # Use sort_keys=True in json.dump? Or create a new dict.
            # json.dump(data, f, sort_keys=True, ...)

            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=True)
            print(f"  Saved updates.")
        else:
            print(f"  No changes needed.")

if __name__ == "__main__":
    harvest()
