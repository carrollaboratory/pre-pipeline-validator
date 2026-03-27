import pytest


@pytest.fixture
def valid_dd_row():
    return {
        "variable_name": "masked_id",
        "description": "Masked ID",
        "data_type": "integer",
        "min": None,
        "max": None,
        "units": None,
        "enumerations": None,
    }


@pytest.fixture
def invalid_dd_row_bad_variable_name():
    return {
        "variable_name": "Xerosis cutis",
        "description": "Xerosis cutis",
        "data_type": "string",
        "min": None,
        "max": None,
        "units": None,
        "enumerations": None,
    }


@pytest.fixture
def invalid_dd_row_numeric_constraints():
    return {
        "variable_name": "age",
        "description": "Age at last encounter",
        "data_type": "string",
        "min": "0",
        "max": None,
        "units": None,
        "enumerations": None,
    }


@pytest.fixture
def invalid_dd_row_bad_data_type():
    return {
        "variable_name": "age",
        "description": "Age at last encounter",
        "data_type": "text",
        "min": None,
        "max": None,
        "units": None,
        "enumerations": None,
    }
