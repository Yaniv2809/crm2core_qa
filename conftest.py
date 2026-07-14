import pytest
import logging
from data_forge.data_generator import TestDataGenerator
from logic.exchange_rate_service import ExchangeRateService
from logic.sync_validator_service import SyncValidatorService

@pytest.fixture(scope="session")
def exchange_rate():
    """
    Fetches the live USD to ILS exchange rate once for the entire test session.
    """
    return ExchangeRateService.get_usd_to_ils_rate()

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment(exchange_rate):
    """
    Automatically runs before any tests start (autouse=True).
    Initializes the databases and injects test data with intentional bugs.
    """
    logging.info("Setting up test databases and generating dynamic test data...")
    generator = TestDataGenerator()
    # Generates 50 records and applies the live exchange rate for calculations
    generator.generate_and_inject_data(exchange_rate=exchange_rate, record_count=50)
    
    yield
    
    logging.info("Test session completed.")

@pytest.fixture
def validator():
    """
    Provides a fresh instance of the SyncValidatorService for each test.
    """
    return SyncValidatorService()