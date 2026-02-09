import os
import json
import requests
import polib

# Constants
UPSTREAM_CACHE_DIR = ".upstream_cache"
MASTER_RO_FILE = "master.ro"

SOURCES = {
    "frappe": "https://raw.githubusercontent.com/frappe/frappe/develop/frappe/locale/main.pot",
    "erpnext": "https://raw.githubusercontent.com/frappe/erpnext/develop/erpnext/locale/main.pot",
    "django": "https://raw.githubusercontent.com/django/django/main/django/conf/locale/en/LC_MESSAGES/django.po",
    "glib": "https://raw.githubusercontent.com/GNOME/glib/main/po/en_GB.po",
}

def ensure_cache_dir():
    if not os.path.exists(UPSTREAM_CACHE_DIR):
        os.makedirs(UPSTREAM_CACHE_DIR)

def download_and_cache_file(project_name, url):
    print(f"Downloading {project_name} from {url}...")
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    # Standardize extension to .po for simplicity, or keep original.
    # But for caching purposes, we just need the file content.
    filename = os.path.join(UPSTREAM_CACHE_DIR, f"{project_name}.po")
    with open(filename, "wb") as f:
        f.write(response.content)
    print(f"Cached {project_name} to {filename}")
    return filename

def load_master_ro():
    if not os.path.exists(MASTER_RO_FILE):
        return {}
    try:
        with open(MASTER_RO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_master_ro(data):
    with open(MASTER_RO_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Updated {MASTER_RO_FILE}")

def merge_into_master(master_data, po_file_path, project_name):
    print(f"Merging strings from {project_name}...")
    try:
        po = polib.pofile(po_file_path)
    except Exception as e:
        print(f"Error reading {po_file_path}: {e}")
        return

    for entry in po:
        msgid = entry.msgid
        if not msgid:
            continue

        if msgid not in master_data:
            master_data[msgid] = {
                "ven": "",
                "status": "todo",
                "source": project_name
            }
        else:
            current_source = master_data[msgid].get("source", "")
            # Split by comma and strip whitespace to handle existing sources correctly
            sources_list = [s.strip() for s in current_source.split(",")] if current_source else []

            if project_name not in sources_list:
                sources_list.append(project_name)
                # Join with ", " for readability
                master_data[msgid]["source"] = ", ".join(sources_list)

def main():
    ensure_cache_dir()
    master_data = load_master_ro()

    for project_name, url in SOURCES.items():
        try:
            cached_file = download_and_cache_file(project_name, url)
            merge_into_master(master_data, cached_file, project_name)
        except Exception as e:
            print(f"Failed to process {project_name}: {e}")

    save_master_ro(master_data)

if __name__ == "__main__":
    main()
