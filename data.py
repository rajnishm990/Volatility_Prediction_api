import sqlite3

import pandas as pd 
import numpy as np
import requests
from config import settings

class AlphaVantageAPI():
    def __init__(self, api_key):
        self.__api_key = api_key

    def get_daily(self,ticker,output_size='full'):
        """Get daily time series of an equity from AlphaVantage API.

        Parameters
        ----------
        ticker : str
            The ticker symbol of the equity.
        output_size : str, optional
            Number of observations to retrieve. "compact" returns the
            latest 100 observations. "full" returns all observations for
            equity. By default "full".

        Returns
        -------
        pd.DataFrame
            Columns are 'open', 'high', 'low', 'close', and 'volume'.
            All columns are numeric.
        """
        url = f"https://alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize={output_size}&apikey={self.__api_key}"
        response = requests.get(url)
        json_data = response.json()
        
        if "Time Series (Daily)" not in json_data:
            raise Exception(f"Invalid api call , Check you ticker : {ticker}")
        data = json_data["Time Series (Daily)"]
        df = pd.DataFrame().from_dict(data,orient='index',dtype=float)
        df.index = pd.to_datetime(df.index)
        df.index.name = "date"
        df.columns = [c.split(". ")[1] for c in df.columns]
    
        return df

class SQLRepository():
    def __init__(self,connection):
        self.connection = connection
    def insert_table(self,table_name,records ,if_exists='fail'):
        """Insert DataFrame into SQLite database as table

        Parameters
        ----------
        table_name : str
        records : pd.DataFrame
        if_exists : str, optional
            How to behave if the table already exists.

            - 'fail': Raise a ValueError.
            - 'replace': Drop the table before inserting new values.
            - 'append': Insert new values to the existing table.

            Dafault: 'fail'

        Returns
        -------
        dict
            Dictionary has two keys:

            - 'transaction_successful', followed by bool
            - 'records_inserted', followed by int
        """
        records_added = records.to_sql(name=table_name,con=self.connection,if_exists=if_exists)
        return {"transaction_successful":True,"records_inserted":records_added}
    
    def read_table(self,table_name,limit=None):
        """Read table from database.

        Parameters
        ----------
        table_name : str
            Name of table in SQLite database.
        limit : int, None, optional
            Number of most recent records to retrieve. If `None`, all
            records are retrieved. By default, `None`.

        Returns
        -------
        pd.DataFrame
            Index is DatetimeIndex "date". Columns are 'open', 'high',
            'low', 'close', and 'volume'. All columns are numeric. """
        if limit:
            sql = f"SELECT * FROM '{table_name}' LIMIT {limit}"
        else:
            sql = f"SELECT * FROM {table_name}"
        df = pd.read_sql(sql=sql,con = self.connection , index_col="date",parse_dates=["date"])
        return df 

        