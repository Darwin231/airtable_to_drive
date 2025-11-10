# airtable to drive

# Airtable → Google Drive Automation

This repository automates the extraction of data from multiple **Airtable bases** and uploads them as spreadsheets to a **Google Drive (Workspace)** folder.

The process runs daily via **GitHub Actions**, authenticating securely with a **Google Service Account**.

---

## 🚀 Features
- Fetch data from multiple Airtable bases/tables.
- Convert Airtable records into `.xlsx` spreadsheets.
- Upload results to a target Google Drive folder.
- Automated daily run using GitHub Actions.
- Supports both **My Drive** and **Shared Drives** (Workspace).
- Environment-based configuration for flexible deployments.

---

## 🧩 Project Structure



---

## ⚙️ Environment Variables

| Variable | Description | Required |
|-----------|--------------|-----------|
| `AIRTABLE_API` | Airtable Personal Access Token (PAT) | ✅ |
| `BASE_ID` | Main Airtable base ID | ✅ |
| `TABLE_NAME` | Default Airtable table name | ✅ |
| `FOLDER_ID` | Google Drive folder ID (destination) | ✅ |
| `GCP_QUOTA_PROJECT` | Google Cloud project ID (used by Drive API) | ✅ |
| `KHAWA_BASE_ID` | Airtable base ID for Khawa data | ✅ |
| `KHAWA_PRODUCERS_TABLE_NAME` | Producers table name | ✅ |
| `KHAWA_BENEFICIO_TABLE_NAME` | Beneficio table name | ✅ |
| `KHAWA_CAFE_TABLE_NAME` | Coffee table name | ✅ |
| `KHAWA_ROASTERS_TABLE_NAME` | Roasters table name | ✅ |
| `KHAWA_CAFETERIAS_TABLE_NAME` | Cafeterías table name | ✅ |

Optional:
- `GOOGLE_DELEGATE_USER`: (only if using domain-wide delegation)
- `GOOGLE_APPLICATION_CREDENTIALS`: local path to service account JSON (set automatically in Actions)

---

## 🔐 Secrets for GitHub Actions

In your repository → **Settings → Secrets and variables → Actions**, add:

| Secret | Description |
|---------|--------------|
| `AIRTABLE_API` | Airtable API token |
| `AIRTABLE_BASE_ID` | Airtable base ID |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Contents of the Google Service Account JSON |
| `GOOGLE_DRIVE_FOLDER_ID` | Folder where files will be uploaded |
| `GCP_QUOTA_PROJECT` | Quota project (Google Cloud) |

> 🔒 Secrets are encrypted and available only to the workflow at runtime.


## ☁️ GitHub Actions Workflow

Located at:
.github/workflows/daily-airtable-export.yml

**Key features:**
- Runs daily at Friday 09:00 UTC (Europa/Madrid = 10:00/11:00).  
- Supports manual trigger via *Run workflow* button.  
- Installs Python dependencies.  
- Authenticates using your Google Service Account.  
- Executes the export/upload process.
