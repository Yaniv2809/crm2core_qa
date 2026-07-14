import requests
import logging
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class APIClient:
    """
    מחלקה גנרית לביצוע קריאות רשת.
    מטרתה לרכז את כל הטיפול בשגיאות HTTP ותצורת הקריאות במקום אחד.
    """
    
    @staticmethod
    def get(url: str, params: dict = None, headers: dict = None, timeout: int = 10) -> dict:
        """
        מבצעת קריאת GET ומחזירה את התשובה כ-JSON.
        
        :param url: הכתובת אליה פונים
        :param params: פרמטרים שיתווספו ל-URL (Query Params)
        :param headers: כותרות (Headers) לקריאה
        :param timeout: זמן מקסימלי להמתנה בשניות
        :return: מילון (dict) המייצג את תשובת ה-JSON
        """
        logger.debug(f"Sending GET request to: {url} | Params: {params}")
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=timeout)
            
            # פונקציה קריטית: זורקת שגיאה אם הסטטוס קוד הוא 4xx או 5xx
            response.raise_for_status()
            
            return response.json()
            
        except RequestException as e:
            # תפיסת כל שגיאות הרשת (Timeout, Connection Error, HTTP Error)
            logger.error(f"API Request failed for URL {url}. Error: {e}")
            
            # אנחנו זורקים את השגיאה הלאה, כדי שהטסט יכשל ולא ימשיך לרוץ על נתונים ריקים
            raise RuntimeError(f"Failed to fetch data from API: {e}")