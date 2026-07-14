import requests
import logging
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class APIClient:
    """ A simple API client to handle GET requests and return JSON responses."""
    
    @staticmethod
    def get(url: str, params: dict = None, headers: dict = None, timeout: int = 10) -> dict:
        """
        Sends a GET request and returns the response as JSON.
        
        :param url: The URL to request
        :param params: Parameters to include in the URL (Query Params)
        :param headers: Headers for the request
        :param timeout: Maximum time to wait for a response in seconds
        :return: A dictionary representing the JSON response
        """
        logger.debug(f"Sending GET request to: {url} | Params: {params}")
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=timeout)
            
            # Critical function: Raises an error if the status code is 4xx or 5xx
            response.raise_for_status()
            
            return response.json()
            
        except RequestException as e:
            # Capturing all network errors (Timeout, Connection Error, HTTP Error)
            logger.error(f"API Request failed for URL {url}. Error: {e}")
            
            # We raise the error further, so the test fails and doesn't continue running on empty data
            raise RuntimeError(f"Failed to fetch data from API: {e}")