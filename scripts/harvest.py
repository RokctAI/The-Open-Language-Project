import os
import glob
import json
import requests
import polib
import re

# Configuration
GROUPS = {
    "apps.ro": [
        "https://raw.githubusercontent.com/frappe/frappe/develop/frappe/locale/main.pot",
        "https://raw.githubusercontent.com/frappe/erpnext/develop/erpnext/locale/main.pot",
    ],
    "system.ro": [
        "https://raw.githubusercontent.com/django/django/main/django/conf/locale/en/LC_MESSAGES/django.po",
        "https://raw.githubusercontent.com/GNOME/glib/main/po/en_GB.po",
    ]
}

TRANSLATIONS_DIR = "translations"
UPSTREAM_CACHE_DIR = ".upstream_cache"


def ensure_dirs():
    if not os.path.exists(UPSTREAM_CACHE_DIR):
        os.makedirs(UPSTREAM_CACHE_DIR)
    if not os.path.exists(TRANSLATIONS_DIR):
        os.makedirs(TRANSLATIONS_DIR)


def is_valid_lang_code(code):
    # Basic validation: 2-3 lowercase letters, optionally with a region (e.g.,
    # pt_BR)
    return re.match(r"^[a-z]{2,3}(_[A-Z]{2})?$", code) is not None


def harvest():
    ensure_dirs()

    # 1. Collect unique keys for each group
    group_keys = {
        "apps.ro": set(),
        "system.ro": set()
    }

    for filename, urls in GROUPS.items():
        for url in urls:
            try:
                print(f"Fetching {url} for {filename}...")
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                # Save temporarily for polib
                temp_filename = os.path.join(UPSTREAM_CACHE_DIR, "temp.po")
                with open(temp_filename, "wb") as f:
                    f.write(response.content)

                po = polib.pofile(temp_filename)
                count = 0
                for entry in po:
                    if entry.msgid:
                        group_keys[filename].add(entry.msgid)
                        count += 1
                print(f"  Found {count} keys.")

            except Exception as e:
                print(f"Error processing {url}: {e}")

        print(f"Total unique keys for {filename}: {len(group_keys[filename])}")

    # 2. Update translation files in each language folder
    if not os.path.exists(TRANSLATIONS_DIR):
        os.makedirs(TRANSLATIONS_DIR)

    lang_dirs = [
        d for d in os.listdir(TRANSLATIONS_DIR) if os.path.isdir(
            os.path.join(
                TRANSLATIONS_DIR,
                d))]

    for lang in lang_dirs:
        if not is_valid_lang_code(lang):
            print(f"Skipping invalid language folder: {lang}")
            continue

        lang_path = os.path.join(TRANSLATIONS_DIR, lang)
        print(f"Processing language: {lang}")

        for ro_filename, keys in group_keys.items():
            ro_path = os.path.join(lang_path, ro_filename)

            # Load existing data or create new
            try:
                if os.path.exists(ro_path):
                    with open(ro_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                else:
                    data = {}
            except (FileNotFoundError, json.JSONDecodeError):
                data = {}

            modified = False
            for msgid in keys:
                if msgid not in data:
                    data[msgid] = ""
                    modified = True

            if modified:
                print(f"  Updating {ro_filename}...")
                with open(ro_path, 'w', encoding='utf-8') as f:
                    json.dump(
                        data,
                        f,
                        indent=4,
                        ensure_ascii=False,
                        sort_keys=True)
            else:
                print(f"  No changes needed for {ro_filename}.")


if __name__ == "__main__":
    harvest()
