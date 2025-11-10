from dotenv import load_dotenv
from pathlib import Path
import os

from src.storage.functions import GPCUtils
from src.extraction.functions import AirtableExtraction

def run_upload():
    try:
        env_path = Path(__file__).resolve().parents[2] / "conf" / ".env"
        load_dotenv(env_path)
    except Exception as e:
        print(e)

    api_key = os.environ.get('AIRTABLE_API')
    base_id = os.environ.get('BASE_ID')
    table_name = os.environ.get('TABLE_NAME')
    folder_id = os.environ.get('FOLDER_ID')
    gpc_quota_project = os.environ.get('GCP_QUOTA_PROJECT')
    KHAWA_BASE_ID = os.environ.get('KHAWA_BASE_ID')
    KHAWA_PRODUCERS_TABLE_NAME = os.environ.get('KHAWA_PRODUCERS_TABLE_NAME')
    KHAWA_BENEFICIO_TABLE_NAME = os.environ.get('KHAWA_BENEFICIO_TABLE_NAME')
    KHAWA_CAFE_TABLE_NAME = os.environ.get('KHAWA_CAFE_TABLE_NAME')
    KHAWA_ROASTERS_TABLE_NAME = os.environ.get('KHAWA_ROASTERS_TABLE_NAME')
    KHAWA_CAFETERIAS_TABLE_NAME = os.environ.get('KHAWA_CAFETERIAS_TABLE_NAME')

    tables_to_upload = {
        base_id: {table_name: 'eventos'},
        KHAWA_BASE_ID: {
            KHAWA_PRODUCERS_TABLE_NAME : 'productores',
            KHAWA_BENEFICIO_TABLE_NAME : 'beneficio',
            KHAWA_CAFE_TABLE_NAME : 'cafes',
            KHAWA_ROASTERS_TABLE_NAME : 'roasters',
            KHAWA_CAFETERIAS_TABLE_NAME : 'cafeterias'
        },
    }

    for base, tables in tables_to_upload.items():
        for table, name in tables.items():
            print("base: ", base)
            print("table: ", table)
            print("name: ", name)

            airtable_df = AirtableExtraction(API=api_key, BASE_ID=base, TABLE_NAME=table)
            df = airtable_df.df_extraction()

            gpc = GPCUtils(folder_id=folder_id, quota_project=gpc_quota_project)
            gpc.auth()
            gpc.upload_dataframe_xlsx(df=df, drive_filename=f"{name}.xlsx")


def main():
    run_upload()

if __name__ == "__main__":
    main()
