# Excel Processor

A local web application to view and edit Excel files interactively, with a pluggable storage provider system that supports local files, Microsoft 365 (SharePoint / OneDrive for Business), and a template for future Google Sheets support.

## Features

- Read and display Excel sheets in a browser table
- Edit cell values and write them back to the source file
- Pluggable provider architecture — swap the backend without touching the UI
- Microsoft 365 OAuth login via MSAL (device-flow / SPA)
- No database — the Excel file **is** the data store

## Providers

| Provider | Where the file lives | Auth required |
|---|---|---|
| `local` | Local disk (incl. OneDrive / iCloud / Dropbox sync folder) | No |
| `microsoft365` | SharePoint Online / OneDrive for Business sharing link | Yes (Azure AD SPA) |
| `google_sheets` | Google Drive spreadsheet *(template — not yet implemented)* | — |
 
## Requirements

- Python 3.12+
- `uv` package manager (`brew install uv` or https://docs.astral.sh/uv/)

## Setup

### 1. Choose your provider and create `.env`

```bash
# Local file (simplest, no auth needed):
cp .env.example.local .env

# Microsoft 365:
cp .env.example.m365 .env

# See .env.example for a full description of all options
```

Edit `.env` and fill in your values (file path, Azure client ID, etc.).

### 2. Start the server

```bash
./start.sh
```

The script will:
1. Create a Python virtual environment (`.venv`) if it doesn't exist
2. Install all dependencies with `uv sync`
3. Activate the virtual environment
4. Start the FastAPI server on `http://localhost:8000`
5. Open the application in your default browser

### 3. Use the app

- **Dashboard** → `http://localhost:8000` — landing page with all mini-apps
- **Excel Processor** → `http://localhost:8000/02-excelprocessor/processor.html`

## Project Structure

```
excel-processor/
├── app/
│   ├── main.py                  # FastAPI application entry point
│   ├── core/
│   │   ├── config.py            # Pydantic settings (reads .env)
│   │   └── providers/           # Pluggable provider implementations
│   │       ├── base.py          # Abstract ExcelProvider interface
│   │       ├── local_file.py    # Local disk provider (openpyxl)
│   │       └── microsoft365.py  # Microsoft Graph API provider
│   ├── routers/
│   │   └── excel.py             # /api/excel/* REST endpoints
│   └── static/                  # Frontend (HTML / CSS / JS)
│       ├── index.html           # Dashboard
│       ├── 01-general/          # Shared styles and shell
│       └── 02-excelprocessor/   # Excel Processor UI
├── tests/
├── pyproject.toml
├── .env.example                 # Provider selection guide
├── .env.example.local           # Local file provider template
├── .env.example.m365            # Microsoft 365 provider template
└── .env.example.googlesheets    # Google Sheets template (not yet implemented)
```

## Development

```bash
# Format + lint + type-check
uv run ruff format app tests && uv run ruff check app tests

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=app
```

## Microsoft 365 Setup (one-time)

1. Go to https://portal.azure.com → **App registrations** → **New registration**
2. Name: `Excel Processor`
3. Supported account types: *Accounts in any organizational directory*
4. Redirect URI: **Single-page application (SPA)** → `http://localhost:8000`
5. Copy the **Application (client) ID** into `AZURE_CLIENT_ID` in `.env`
6. **API permissions** → Add → Microsoft Graph → Delegated:
   - `Files.ReadWrite`
   - `Sites.ReadWrite.All`
7. Grant admin consent (or ask your admin)
