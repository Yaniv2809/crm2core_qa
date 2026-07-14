import pytest
import allure

@allure.feature("Data Integrity")
@allure.story("Financial Conversion Accuracy")
@pytest.mark.parametrize("expected_mismatch_count", [0])
def test_loan_amount_conversion_accuracy(validator, exchange_rate, expected_mismatch_count):
    """
    Verifies that the USD to ILS conversion in the Core DB matches the live API rate.
    Expected to fail due to the intentional math bug injected into CRM-1010.
    """
    mismatches = validator.get_amount_conversion_mismatches(exchange_rate)
    
    error_msg = f"Financial mismatch detected! Found {len(mismatches)} calculation errors. Details: {mismatches}"
    
    assert len(mismatches) == expected_mismatch_count, error_msg