import sqlite3
import logging

# הגדרת לוגר פשוט כדי שנוכל לראות איזה שאילתות רצות מאחורי הקלעים
logger = logging.getLogger(__name__)

class DBClient:
    def __init__(self, db_path: str):
        """
        מקבלת את נתיב מסד הנתונים בעת יצירת המופע (Instance).
        כך נוכל להשתמש באותה מחלקה גם עבור ה-CRM וגם עבור ה-Bank Core.
        """
        self.db_path = db_path

    def _get_connection(self):
        """פונקציה פנימית ליצירת חיבור למסד הנתונים"""
        return sqlite3.connect(self.db_path)

    def fetch_all(self, query: str, params: tuple = ()) -> list:
        """
        מבצעת שאילתת שליפה (SELECT) ומחזירה את התוצאות.
        :param query: מחרוזת שאילתת ה-SQL
        :param params: פרמטרים להזרקה למניעת SQL Injection
        :return: רשימה של מילונים (Dictionaries) המייצגים את הרשומות
        """
        with self._get_connection() as conn:
            # הגדרה קריטית לאוטומציה: מחזיר מילון במקום Tuple רגיל
            conn.row_factory = sqlite3.Row 
            cursor = conn.cursor()
            
            logger.debug(f"Executing query: {query} | Params: {params}")
            cursor.execute(query, params)
            
            # המרה חכמה של התוצאות לרשימה של מילונים (Key-Value)
            return [dict(row) for row in cursor.fetchall()]

    def execute_query(self, query: str, params: tuple = ()):
        """
        מבצעת שאילתות שלא מחזירות נתונים כמו INSERT, UPDATE, DELETE, CREATE TABLE
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()