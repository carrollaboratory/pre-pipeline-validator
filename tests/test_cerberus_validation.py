from unittest.mock import mock_open, patch

from src.pre_pipeline_validator.models.cerberus_validation import (
    csv_to_dicts_chunked,
    run_cerberus_validation,
)
from src.pre_pipeline_validator.models.cerberus_validation.cerb_dd_validation import (
    DataDictionaryValidator,
)
from src.pre_pipeline_validator.schemas.example_data_dictionary import schema


CSV_CONTENT = "variable_name,description,data_type,min,max\nmasked_id,Masked ID,integer,,\nAGE,Age at last encounter,string,,\n"


def test_csv_to_dicts_chunked_returns_rows():
    """Rows from the CSV are returned as dicts with correct values."""
    with patch("builtins.open", mock_open(read_data=CSV_CONTENT)):
        rows = [row for chunk in csv_to_dicts_chunked("fake/path.csv") for row in chunk]
    assert len(rows) == 2
    assert rows[0]["variable_name"] == "masked_id"
    assert rows[1]["description"] == "Age at last encounter"


def test_csv_to_dicts_chunked_normalizes_empty_strings_to_none():
    """Empty string values in the CSV are converted to None."""
    with patch("builtins.open", mock_open(read_data=CSV_CONTENT)):
        rows = [row for chunk in csv_to_dicts_chunked("fake/path.csv") for row in chunk]
    assert rows[0]["min"] is None
    assert rows[0]["max"] is None


def test_run_cerberus_validation_returns_validator_object(valid_dd_row):
    """run_cerberus_validation returns a Validator object with errors and document_error_tree attributes."""
    v = run_cerberus_validation(schema, valid_dd_row, validator_class=DataDictionaryValidator)
    assert hasattr(v, "errors")
    assert hasattr(v, "document_error_tree")
