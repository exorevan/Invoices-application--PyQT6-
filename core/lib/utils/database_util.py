import logging
import sqlite3

from config import DEFAULT_DB_PATH


class DBUtil:
    def __init__(self):
        """
        Initializes the DBUtil object by establishing a connection to the SQLite database
        and initializing the cursor. It also resets the sequence values for the 'goods' and 'invoices' tables.
        """
        self.connection = sqlite3.connect(DEFAULT_DB_PATH)
        self.cursor = self.connection.cursor()
        self.update("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='goods';")
        self.update("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='invoices';")

    def select(self, query: str) -> list:
        """
        Executes a select query and returns the results as a list of tuples.

        Args:
            query (str): The select query to execute.

        Returns:
            list: The results of the select query as a list of tuples.
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
            return self.cursor.fetchall()
        except Exception as e:
            logging.error(f"Error executing select query: {e}")
            raise

    def update(self, query: str) -> None:
        """
        Executes an update query to modify the database.

        Args:
            query (str): The update query to execute.
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except Exception as e:
            logging.error(f"Error executing update query: {e}")
            raise
