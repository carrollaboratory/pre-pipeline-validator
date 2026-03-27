import pytest
from src.validator.models.cerberus_validation.schema_builder import csv_to_cerberus_schema


@pytest.fixture
def dd_rows():
    return [
        {"variable_name": "age", "data_type": "integer", "required": "TRUE",
         "min": "0", "max": "120", "enumerations": None},
        {"variable_name": "status", "data_type": "string", "required": "FALSE",
         "min": None, "max": None, "enumerations": "active;inactive"},
        {"variable_name": "score", "data_type": "float", "required": "TRUE",
         "min": "0.0", "max": "1.0", "enumerations": None},
    ]


def test_data_type_is_mapped(dd_rows):
    """data_type values from the DD are converted to their Cerberus type equivalents."""
    schema = csv_to_cerberus_schema(dd_rows)
    assert schema["age"]["type"] == "integer"
    assert schema["status"]["type"] == "string"
    assert schema["score"]["type"] == "float"


def test_min_max_set_for_numeric(dd_rows):
    """min and max are included in the schema only for numeric fields, cast to the correct type."""
    schema = csv_to_cerberus_schema(dd_rows)
    assert schema["age"]["min"] == 0
    assert schema["age"]["max"] == 120


def test_min_max_not_set_for_string(dd_rows):
    """min and max are omitted from the schema for non-numeric fields."""
    schema = csv_to_cerberus_schema(dd_rows)
    assert "min" not in schema["status"]
    assert "max" not in schema["status"]


def test_row_without_variable_name_is_skipped():
    """Rows with no variable_name are silently skipped and produce no schema entry."""
    rows = [{"variable_name": None, "data_type": "string"}]
    schema = csv_to_cerberus_schema(rows)
    assert schema == {}

