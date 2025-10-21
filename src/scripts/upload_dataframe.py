import os

from pathlib import Path
from dotenv import load_dotenv
from src.storage.functions import GPCUtils
from src.extraction.functions import AirtableExtraction


def run_upload():
    try:
        # build an absolute path safely
        env_path = Path(__file__).resolve().parents[2] / "conf" / ".env"

        # load_dotenv returns True if it found and loaded something
        if load_dotenv(env_path):
            print(f"✅ .env loaded from {env_path}")
        else:
            print(f"⚠️  No .env file found at {env_path}")

    except Exception as e:
        print(f"⚠️ dotenv load failed: {e}")
        pass

    # Community table access
    api_key = os.environ.get('AIRTABLE_API')
    base_id = os.environ.get('BASE_ID')
    table_name = os.environ.get('TABLE_NAME')
    folder_id = os.environ.get('FOLDER_ID')
    gpc_quota_project = os.environ.get('GCP_QUOTA_PROJECT')

    # Cloud paths
    base_conf = os.path.abspath(os.path.join(os.path.dirname(os.getcwd()), 'conf'))
    token_path = os.path.join(base_conf, 'tokens.json')


    airtable_df = AirtableExtraction(
        API=api_key,
        BASE_ID=base_id,
        TABLE_NAME=table_name
    )

    df = airtable_df.df_extraction()

    # Google cloud storage access
    gpc = GPCUtils(folder_id = folder_id,
                   quota_project = gpc_quota_project)
    

    # Check token and authenticate
    if os.path.exists(token_path):
        gpc.auth()

    # Drive upload
    gpc.upload_dataframe_xlsx(
        df = df,
        drive_filename = "airtable_communityt_data.xlsx",
    )


def main():
    # keep `main()` tiny so it's easy to test
    run_upload()

if __name__ == "__main__":
    main()

