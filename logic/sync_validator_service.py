import logging
from infra.db_client import DBClient
from config.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class SyncValidatorService:
    def __init__(self):
        """
        מאתחל את החיבור למסד הנתונים של הבנק (היעד),
        ומצרף אליו את מסד הנתונים של ה-CRM (המקור) כדי לאפשר שאילתות משותפות.
        """
        self.bank_db_path = ConfigManager.get_bank_db_path()
        self.crm_db_path = ConfigManager.get_crm_db_path()
        
        # אנחנו יוצרים DBClient אחד שמתחבר לבנק
        self.db_client = DBClient(self.bank_db_path)
        self._attach_crm_db()

    def _attach_crm_db(self):
        """
        מצרף את קובץ ה-CRM כאליאס (crm_db) לתוך החיבור הקיים של הבנק.
        זה מה שמאפשר לנו לעשות INNER JOIN ו-LEFT JOIN בין שני קבצים שונים.
        """
        query = f"ATTACH DATABASE '{self.crm_db_path}' AS crm_db;"
        self.db_client.execute_query(query)
        logger.debug("Successfully attached CRM database to Bank Core connection.")

    def get_missing_records_in_core(self) -> list:
        """
        מחזיר רשימה של כל בקשות האשראי שקיימות ב-CRM אך מעולם לא סונכרנו ל-Core.
        """
        query = """
            SELECT S.Request_ID, S.First_Name, S.Last_Name
            FROM crm_db.Source_Requests S
            LEFT JOIN Target_Database T ON S.Request_ID = T.CRM_Ref_ID
            WHERE T.CRM_Ref_ID IS NULL;
        """
        return self.db_client.fetch_all(query)

    def get_amount_conversion_mismatches(self, exchange_rate: float) -> list:
        """
        מוצא רשומות שסונכרנו, אבל חישוב ההמרה מדולר לשקל היה שגוי מעבר לסטייה המותרת.
        """
        tolerance = ConfigManager.get_allowed_deviation()
        
        query = """
            SELECT 
                S.Request_ID, 
                S.Loan_Amount_USD AS Source_USD, 
                T.Loan_Amount_ILS AS Target_ILS,
                ROUND(S.Loan_Amount_USD * ?, 2) AS Expected_ILS
            FROM crm_db.Source_Requests S
            INNER JOIN Target_Database T ON S.Request_ID = T.CRM_Ref_ID
            -- שימוש ב-ABS (ערך מוחלט) כדי למצוא סטיות מתמטיות מעבר למותר
            WHERE ABS(T.Loan_Amount_ILS - ROUND(S.Loan_Amount_USD * ?, 2)) > ?;
        """
        # נעביר את שער החליפין פעמיים (עבור ה-SELECT ועבור ה-WHERE) ואת הסטייה המותרת
        return self.db_client.fetch_all(query, (exchange_rate, exchange_rate, tolerance))