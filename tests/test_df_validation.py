from src.validator.models.cerberus_validation.df_validation import (
    _build_row_description,
    _build_description,
)


def test_build_row_description_few_rows():
    """Row numbers are joined into a comma-separated string."""
    assert _build_row_description([2, 3, 4]) == "Failing rows: 2,3,4"


def test_build_row_description_truncates_after_ten():
    """Lists longer than 10 rows are truncated with a trailing ellipsis."""
    rows = list(range(2, 15))
    result = _build_row_description(rows)
    assert result.endswith(",...")
    assert result.count(",") == 10


def test_build_description_min():
    """Min rule produces a message stating the minimum value for the field."""
    result = _build_description("age", "min", 0, [3, 4])
    assert result == "The minimum value for age is 0. Failing rows: 3,4"


def test_build_description_max():
    """Max rule produces a message stating the maximum value for the field."""
    result = _build_description("age", "max", 120, [5])
    assert result == "The maximum value for age is 120. Failing rows: 5"


def test_build_description_type():
    """Type rule produces a message naming the expected data type."""
    result = _build_description("age", "type", "integer", [2])
    assert result == "age must be of type 'integer'. Failing rows: 2"


def test_build_description_allowed():
    """Allowed rule produces a message listing the permitted values."""
    result = _build_description("status", "allowed", ["a", "b"], [10])
    assert result == "status must be one of the allowed values: ['a', 'b']. Failing rows: 10"


def test_build_description_required():
    """Required rule produces a message indicating the field cannot be empty."""
    result = _build_description("name", "required", None, [4, 5])
    assert result == "name is required and cannot be empty. Failing rows: 4,5"