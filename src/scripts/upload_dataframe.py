from dotenv import load_dotenv
from pathlib import Path
import os

from src.storage.functions import GPCUtils
from src.extraction.functions import AirtableExtraction

def run_upload():
    # Silenciar warning del .env si no existe
    try:
        env_path = Path(__file__).resolve().parents[2] / "conf" / ".env"
        load_dotenv(env_path)  # no imprimir nada si no existe
    except Exception:
        pass

    api_key = os.environ.get('AIRTABLE_API')
    base_id = os.environ.get('BASE_ID')
    table_name = os.environ.get('TABLE_NAME')
    folder_id = os.environ.get('FOLDER_ID')
    gpc_quota_project = os.environ.get('GCP_QUOTA_PROJECT')

    airtable_df = AirtableExtraction(API=api_key, BASE_ID=base_id, TABLE_NAME=table_name)
    df = airtable_df.df_extraction()

    gpc = GPCUtils(folder_id=folder_id, quota_project=gpc_quota_project)
    gpc.auth()  # <-- siempre

    gpc.upload_dataframe_xlsx(
        df=df,
        drive_filename="airtable_communityt_data.xlsx",
    )

def main():
    run_upload()

if __name__ == "__main__":
    main()
