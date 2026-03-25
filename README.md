# Open Language Project

This project aims to build a translation system for an AI-first ERP. It automatically harvests translation strings from major open-source projects into a simplified, grouped architecture for easy translation.

## Nature of the Project

The Open Language Project is a specialized translation harvester and synchronization tool. Its primary goal is to provide high-quality localized translations for an AI-first ERP system by leveraging translation keys from established open-source ecosystems.

By aggregating keys from projects like Frappe, ERPNext, Django, and GNOME, this repository serves as a centralized bridge. It ensures that the ERP system has access to a broad range of common and domain-specific terms, which can then be translated into local languages (such as Tshivenda) to make the ERP more accessible.

## Repository Structure

The project uses a "Clean" and "Grouped" architecture, where translations are stored directly in language-specific folders without a central master database.

```
.
├── .github/workflows/
│   └── harvester.yml      # GitHub Action (Weekly Schedule)
├── scripts/
│   ├── harvest.py         # Syncs upstream keys into local translations
│   └── build.py           # Exports translations to CSV
├── translations/          # Root folder for all languages
│   └── ve/                # Language Code (e.g., Venda)
│       ├── apps.ro        # Keys from Frappe & ERPNext
│       └── system.ro      # Keys from Django & GNOME
└── requirements.txt
```

## How It Works

This repository acts as an automated bridge between upstream open-source projects and the ERP's translation system.

1.  **Harvesting**: The `scripts/harvest.py` script fetches `.pot` and `.po` files from upstream sources:
    *   **Apps**: Frappe, ERPNext -> `apps.ro`
    *   **System**: Django, GNOME GLib -> `system.ro`
2.  **Merging**: It iterates through all valid language folders in `translations/` (e.g., `ve`, `zu`) and adds any *new* keys found upstream.
    *   **Safety**: Existing translations are *never* overwritten.
    *   **Format**: Keys are stored as simple JSON Key-Value pairs: `"English Phrase": "Translation"`. New keys have empty values.
3.  **Building**: The `scripts/build.py` script aggregates all populated translations (non-empty values) from a language folder into a single CSV file.

## Getting Started

### Prerequisites

*   Python 3.x
*   Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Adding a New Language

To start translating a new language (e.g., Afrikaans `af`):

1.  Create a folder with the language code in `translations/`:
    ```bash
    mkdir translations/af
    ```
2.  Run the harvester to populate the initial files:
    ```bash
    python scripts/harvest.py
    ```
    This will create `translations/af/apps.ro` and `translations/af/system.ro` with all available keys.

### Running the Harvester Manually

To fetch the latest keys from upstream and update all language folders:

```bash
python scripts/harvest.py
```

### Exporting Translations

To export completed translations to a CSV file (e.g., for Venda `ve`):

```bash
python scripts/build.py ve
```

This will generate `ve.csv` containing only the translated keys.

## Automation

The project includes a GitHub Action (`.github/workflows/harvester.yml`) that runs **every Monday at 00:00 UTC**. It automatically:
1.  Runs the harvester script.
2.  Commits any new keys found to the repository.

This ensures the translation files are always up-to-date with the latest upstream changes.
