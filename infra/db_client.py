import sqlite3
import logging

# configuring the logger for this module
logger = logging.getLogger(__name__)

class DBClient:
    def __init__(self, db_path: str):
        """Initializes the DBClient with the path to the SQLite database."""

        self.db_path = db_path

    def _get_connection(self):
        """Establishes a connection to the SQLite database."""
        return sqlite3.connect(self.db_path)

    def fetch_all(self, query: str, params: tuple = ()) -> list:
        """
        Executes a SELECT query and returns the results.
        :param query: The SQL query string
        :param params: Parameters for the query to prevent SQL Injection
        :return: A list of dictionaries representing the rows
        """
        with self._get_connection() as conn:
            # Setting the row factory to sqlite3.Row allows us to access columns by name
            conn.row_factory = sqlite3.Row 
            cursor = conn.cursor()
            
            logger.debug(f"Executing query: {query} | Params: {params}")
            cursor.execute(query, params)
            
            # converting the results to a list of dictionaries (Key-Value)
            return [dict(row) for row in cursor.fetchall()]

    def execute_query(self, query: str, params: tuple = ()):
        """
        Executes queries that do not return data, such as INSERT, UPDATE, DELETE, CREATE TABLE
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()