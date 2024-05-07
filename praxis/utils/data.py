
import sqlite3
import pandas as pd
from typing import List, Dict, Any

class Data:
  """
  Data class to interact with the database
  """

  def __init__(self, db_file: str):
    """
    Initialize the Data class.

    Args:
        db_file (str): The path to the SQLite database file.
    """
    self.db_file = db_file
    self.conn = sqlite3.connect(self.db_file)
    self.cursor = self.conn.cursor()

  async def create_table(self, table_name: str, columns: List[str]):
    """
    Create a new table in the database.

    Args:
        table_name (str): The name of the table to be created.
        columns (List[str]): A list of column names for the table.
    """
    columns = ", ".join(columns)
    self.cursor.execute(f"CREATE TABLE {table_name} ({columns})")
    self.conn.commit()

  async def insert_data(self, table_name: str, data: Dict[str, Any]):
    """
    Insert data into a table in the database.

    Args:
        table_name (str): The name of the table to insert data into.
        data (Dict[str, Any]): A dictionary containing the data to be inserted, where the keys are \
        column names and the values are the corresponding values.
    """
    columns = ", ".join(data.keys())
    values = ", ".join([f"'{v}'" for v in data.values()])
    self.cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({values})")
    self.conn.commit()

  async def read_data(self, table_name: str):
    """
    Read data from a table in the database and return it as a pandas DataFrame.

    Args:
        table_name (str): The name of the table to read data from.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the data from the table.
    """
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", self.conn)
    return df

  async def update_data(self, table_name: str, data: Dict[str, Any], condition: str):
    """
    Update data in a table in the database.

    Args:
        table_name (str): The name of the table to update data in.
        data (Dict[str, Any]): A dictionary containing the data to be updated, where the keys are \
        column names and the values are the new values.
        condition (str): The condition to filter the rows to be updated.
    """
    data = ", ".join([f"{k} = '{v}'" for k, v in data.items()])
    self.cursor.execute(f"UPDATE {table_name} SET {data} WHERE {condition}")
    self.conn.commit()

  async def delete_data(self, table_name: str, condition: str):
    """
    Delete data from a table in the database.

    Args:
        table_name (str): The name of the table to delete data from.
        condition (str): The condition to filter the rows to be deleted.
    """
    self.cursor.execute(f"DELETE FROM {table_name} WHERE {condition}")
    self.conn.commit()

  async def execute_query(self, query: str):
    """
    Execute a custom SQL query on the database.

    Args:
        query (str): The SQL query to be executed.
    """
    self.cursor.execute(query)
    self.conn.commit()

  async def drop_table(self, table_name: str):
    """
    Drop a table from the database.

    Args:
        table_name (str): The name of the table to be dropped.
    """
    self.cursor.execute(f"DROP TABLE {table_name}")
    self.conn.commit()

  async def get_table_columns(self, table_name: str):
    """
    Get the column names of a table in the database.

    Args:
        table_name (str): The name of the table to get the column names from.

    Returns:
        List: A list of column names.
    """
    self.cursor.execute(f"PRAGMA table_info({table_name})")
    columns = self.cursor.fetchall()
    return columns

  async def get_tables(self):
    """
    Get the names of all tables in the database.

    Returns:
        List: A list of table names.
    """
    self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = self.cursor.fetchall()
    return tables

  async def get_table_data(self, table_name: str):
    """
    Get all data from a table in the database.

    Args:
        table_name (str): The name of the table to get the data from.

    Returns:
        List: A list of tuples, where each tuple represents a row of data from the table.
    """
    self.cursor.execute(f"SELECT * FROM {table_name}")
    data = self.cursor.fetchall()
    return data

  async def _get_table_data_as(self, table_name: str, data_type: str):
    """
    Get table data in the specified format.

    Args:
        table_name (str): The name of the table to get the data from.
        data_type (str): The format to return the data in. Valid values are "df" (pandas\
        DataFrame), "dict" (list of dictionaries), and "list" (list of lists).

    Returns:
        pd.DataFrame or List: The table data in the specified format.
    """
    self.cursor.execute(f"SELECT * FROM {table_name}")
    data = self.cursor.fetchall()
    df = pd.DataFrame(data)
    if data_type == "df":
      return df
    elif data_type == "dict":
      data = df.to_dict(orient="records")
      return data
    elif data_type == "list":
      data = df.values.tolist()
      return data
    else:
      return data

  async def get_table_data_as_df(self, table_name: str):
    """
    Get table data as a pandas DataFrame.

    Args:
        table_name (str): The name of the table to get the data from.

    Returns:
        pd.DataFrame: The table data as a pandas DataFrame.
    """
    return await self._get_table_data_as(table_name, "df")

  async def get_table_data_as_dict(self, table_name: str):
    """
    Get table data as a list of dictionaries.

    Args:
        table_name (str): The name of the table to get the data from.

    Returns:
        List: The table data as a list of dictionaries.
    """
    return await self._get_table_data_as(table_name, "dict")

  async def get_table_data_as_list(self, table_name: str):
    """
    Get table data as a list of lists.

    Args:
        table_name (str): The name of the table to get the data from.

    Returns:
        List: The table data as a list of lists.
    """
    return await self._get_table_data_as(table_name, "list")

  async def close(self):
    """
    Close the database connection.
    """
    self.conn.close()
