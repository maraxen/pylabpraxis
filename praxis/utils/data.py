import os
import aiosqlite
import pandas as pd
from typing import List, Dict, Any


class Data:
    """
    Data class to interact with the database asynchronously.
    """

    def __init__(self, conn: aiosqlite.Connection, db_file: str):
        """
        Initialize the Data class.

        Args:
            conn (aiosqlite.Connection): The aiosqlite connection object.
            db_file (str): The path to the SQLite database file.
        """

        self.conn = conn
        self.db_file = db_file
        self.parent_directory = os.path.dirname(db_file)
        self.db_path = os.path.abspath(db_file)

    async def create_table(self, table_name: str, columns: List[str]):
        """
        Create a new table in the database.

        Args:
            table_name (str): The name of the table to be created.
            columns (List[str]): A list of column names for the table.
        """
        columns_str = ", ".join(columns)
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
            )
            await self.conn.commit()

    async def insert_data(self, table_name: str, data: Dict[str, Any]):
        """
        Insert data into a table in the database.

        Args:
            table_name (str): The name of the table to insert data into.
            data (Dict[str, Any]): A dictionary containing the data to be inserted.
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = list(data.values())
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values
            )
            await self.conn.commit()

    async def read_data(self, table_name: str):
        """
        Read data from a table and return it as a pandas DataFrame.

        Args:
            table_name (str): The name of the table to read from.

        Returns:
            pd.DataFrame: A DataFrame containing the data from the table.
        """
        async with self.conn.cursor() as cursor:
            await cursor.execute(f"SELECT * FROM {table_name}")
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return pd.DataFrame.from_records(rows, columns=columns)

    async def update_data(self, table_name: str, data: Dict[str, Any], condition: str):
        """
        Update data in a table.

        Args:
            table_name (str): The name of the table to update.
            data (Dict[str, Any]): A dictionary containing the data to be updated.
            condition (str): The condition to filter the rows to be updated.
        """
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        values = list(data.values())
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                f"UPDATE {table_name} SET {set_clause} WHERE {condition}", values
            )
            await self.conn.commit()

    async def delete_data(self, table_name: str, condition: str):
        """
        Delete data from a table.

        Args:
            table_name (str): The name of the table to delete from.
            condition (str): The condition to filter the rows to be deleted.
        """
        async with self.conn.cursor() as cursor:
            await cursor.execute(f"DELETE FROM {table_name} WHERE {condition}")
            await self.conn.commit()

    async def execute_query(self, query: str):
        """
        Execute a custom SQL query.

        Args:
            query (str): The SQL query to be executed.
        """
        async with self.conn.cursor() as cursor:
            await cursor.execute(query)
            await self.conn.commit()

    async def drop_table(self, table_name: str):
        """
        Drop a table.

        Args:
            table_name (str): The name of the table to be dropped.
        """
        async with self.conn.cursor() as cursor:
            await cursor.execute(f"DROP TABLE {table_name}")
            await self.conn.commit()

    async def get_table_columns(self, table_name: str):
        """
        Get the column names of a table.

        Args:
            table_name (str): The name of the table.

        Returns:
            List: A list of column names.
        """
        async with self.conn.cursor() as cursor:
            await cursor.execute(f"PRAGMA table_info({table_name})")
            columns = await cursor.fetchall()
            return [col[1] for col in columns]

    async def get_tables(self):
        """
        Get the names of all tables in the database.

        Returns:
            List: A list of table names.
        """
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = await cursor.fetchall()
            return [table[0] for table in tables]

    async def get_table_data(self, table_name: str):
        """
        Get all data from a table.

        Args:
            table_name (str): The name of the table.

        Returns:
            List: A list of tuples, where each tuple represents a row of data.
        """
        async with self.conn.cursor() as cursor:
            await cursor.execute(f"SELECT * FROM {table_name}")
            data = await cursor.fetchall()
            return data

    async def _get_table_data_as(self, table_name: str, data_type: str):
        """
        Get table data in the specified format.

        Args:
            table_name (str): The name of the table.
            data_type (str): The format to return the data in ("df", "dict", or "list").

        Returns:
            pd.DataFrame or List: The table data in the specified format.
        """
        async with self.conn.cursor() as cursor:
            await cursor.execute(f"SELECT * FROM {table_name}")
            data = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            df = pd.DataFrame.from_records(data, columns=columns)
        if data_type == "df":
            return df
        elif data_type == "dict":
            return df.to_dict(orient="records")
        elif data_type == "list":
            return df.values.tolist()
        else:
            return data

    async def get_table_data_as_df(self, table_name: str):
        """
        Get table data as a pandas DataFrame.

        Args:
            table_name (str): The name of the table.

        Returns:
            pd.DataFrame: The table data as a pandas DataFrame.
        """
        return await self._get_table_data_as(table_name, "df")

    async def get_table_data_as_dict(self, table_name: str):
        """
        Get table data as a list of dictionaries.

        Args:
            table_name (str): The name of the table.

        Returns:
            List: The table data as a list of dictionaries.
        """
        return await self._get_table_data_as(table_name, "dict")

    async def get_table_data_as_list(self, table_name: str):
        """
        Get table data as a list of lists.

        Args:
            table_name (str): The name of the table.

        Returns:
            List: The table data as a list of lists.
        """
        return await self._get_table_data_as(table_name, "list")

    async def close(self):
        """
        Close the database connection.
        """
        if self.conn:
            await self.conn.close()


async def initialize_data(db_file: str) -> Data:
    """
    Asynchronously creates and initializes a Data instance.
    """
    if not os.path.exists(db_file):
        open(db_file, "w").close()
    conn = await aiosqlite.connect(db_file)
    data = Data(conn, db_file)
    return data
