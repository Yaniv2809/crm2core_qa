import logging
from infra.api_client import APIClient
from config.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class ExchangeRateService:
    
    @classmethod
    def get_usd_to_ils_rate(cls) -> float:
        """
        פונה ל-API החיצוני לקבלת שער הדולר המעודכן מול השקל.
        אם ה-API נכשל, משתמש בערך ברירת המחדל מקובץ ההגדרות.
        """
        url = ConfigManager.get_api_url()
        timeout = ConfigManager.get_api_timeout()
        
        logger.info(f"Fetching live exchange rate from {url}")
        try:
            # משיכת הנתונים דרך שכבת התשתיות שלנו
            response_data = APIClient.get(url=url, timeout=timeout)
            
            # שליפת שער השקל מתוך ה-JSON (rates -> ILS)
            rate = response_data.get("rates", {}).get("ILS")
            
            if not rate:
                raise ValueError("ILS rate not found in the API response.")
                
            logger.info(f"Current USD to ILS rate is: {rate}")
            return float(rate)
            
        except Exception as e:
            # מנגנון Fallback: אם אין אינטרנט או שה-API נפל, ניקח שער דיפולטיבי
            default_rate = ConfigManager.load_config()["business_logic"]["default_ils_rate"]
            logger.error(f"Failed to get live rate. Falling back to default ({default_rate}). Error: {e}")
            return float(default_rate)