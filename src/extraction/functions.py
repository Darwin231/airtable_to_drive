import pandas as pd
from pyairtable import Table


class AirtableExtraction:
    def __init__(self, 
                 API,
                 BASE_ID,
                 TABLE_NAME):
        """
        Initialize the RAGFunctions class.

        :param API: Airtable APIKEY
        :param BASE_ID: Airtable table Base ID
        :param TABLE_NAME: Airtable table name ID
        """
        self.API = API
        self.BASE_ID = BASE_ID
        self.TABLE_NAME = TABLE_NAME

    def df_extraction(self):

        #Table
        table = Table(self.API, self.BASE_ID, self.TABLE_NAME)

        # Table check
        data = [field.get('fields') for field in table.all()]

        # Dataframe creation
        df = pd.DataFrame(data)

        return df