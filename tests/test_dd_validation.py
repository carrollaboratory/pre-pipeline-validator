from src.pre_pipeline_validator.models.cerberus_validation.cerb_dd_validation import (
    DataDictionaryValidator,
)
from src.pre_pipeline_validator.models.cerberus_validation import (
    run_cerberus_validation,
)
from src.pre_pipeline_validator.schemas.example_data_dictionary import schema


def test_numeric_constraints_pass_for_integer():
    """min/max on an integer field does not produce validation errors."""
    row = {
        "variable_name": "age",
        "data_type": "integer",
        "min": "0",
        "max": "120",
        "description": "Age",
        "units": None,
        "enumerations": None,
    }
    v = run_cerberus_validation(schema, row, validator_class=DataDictionaryValidator)
    assert "min" not in v.errors
    assert "max" not in v.errors


def test_numeric_constraints_fail_for_string_with_min():
    """min set on a non-numeric field raises a validation error."""
    row = {
        "variable_name": "label",
        "data_type": "string",
        "min": "5",
        "max": None,
        "description": "Label",
        "units": None,
        "enumerations": None,
    }
    v = run_cerberus_validation(schema, row, validator_class=DataDictionaryValidator)
    assert "min" in v.errors


def test_valid_row_returns_no_errors(valid_dd_row):
    """A well-formed DD row produces no validation errors."""
    v = run_cerberus_validation(
        schema, valid_dd_row, validator_class=DataDictionaryValidator
    )
    assert v.errors == {}


def test_invalid_variable_name_returns_error(invalid_dd_row_bad_variable_name):
    """A variable_name with spaces or illegal characters fails the regex rule."""
    v = run_cerberus_validation(
        schema,
        invalid_dd_row_bad_variable_name,
        validator_class=DataDictionaryValidator,
    )
    assert "variable_name" in v.errors


def test_invalid_data_type_returns_error(invalid_dd_row_bad_data_type):
    """An unrecognized data_type value fails the allowed values rule."""
    v = run_cerberus_validation(
        schema, invalid_dd_row_bad_data_type, validator_class=DataDictionaryValidator
    )
    assert "data_type" in v.errors


def test_numeric_constraints_on_non_numeric_type_returns_error(
    invalid_dd_row_numeric_constraints,
):
    """Setting min on a non-numeric field fails the custom numeric_constraints check."""
    v = run_cerberus_validation(
        schema,
        invalid_dd_row_numeric_constraints,
        validator_class=DataDictionaryValidator,
    )
    assert "min" in v.errors
