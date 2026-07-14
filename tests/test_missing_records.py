import allure

@allure.feature("Data Sync Reliability")
@allure.story("Missing Records Detection")
def test_no_missing_records_in_core_db(validator):
    """
    Verifies that all approved CRM requests successfully synced to the Core DB.
    Expected to fail due to the intentional missing record (CRM-1005).
    """
    missing_records = validator.get_missing_records_in_core()
    
    # Format a clear error message if records are missing
    error_msg = f"Data Loss Detected! Found {len(missing_records)} missing records: {missing_records}"
    
    assert len(missing_records) == 0, error_msg