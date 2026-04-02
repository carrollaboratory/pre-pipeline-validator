import csv
import tempfile
import os
import pytest

from src.deva.models.cerberus_validation.cerb_df_validation import (
    DataFileValidator,
    prepare_and_run_datafile_validation,
)
from src.deva.models.cerberus_validation.schema_builder import csv_to_cerberus_schema

RESOURCES = os.path.join(
    os.path.dirname(__file__), "..", "src", "resources", "examples"
)
FAILING_DD = os.path.join(RESOURCES, "failing_dd.csv")
FAILING_DATAFILE = os.path.join(RESOURCES, "failing_datafile.csv")



# DataFileValidator unit tests



def _make_validator_from_dd(dd_path):
    with open(dd_path, newline="") as f:
        dd_rows = list(csv.DictReader(f))
    schema = csv_to_cerberus_schema(dd_rows)
    expected_fields = {r["variable_name"] for r in dd_rows if r.get("variable_name")}
    return DataFileValidator(schema, expected_fields=expected_fields)


def test_valid_row_passes():
    """A row that satisfies all DD constraints produces no errors."""
    v = _make_validator_from_dd(FAILING_DD)
    v.validate(
        {
            "masked_id": 1,
            "AGE": "one",
            "Acute bronchitis": "1",
            "Acute kidney failure": "0",
            "Xerosis cutis": "1",
        }
    )
    # no schema-rule errors (column errors may fire on first call but checking field-level only)
    assert "AGE" not in v.errors  # "one" is in allowed enumerations


def test_invalid_allowed_value_fails():
    """A value not in the allowed enumerations list produces an error."""
    v = _make_validator_from_dd(FAILING_DD)
    v.validate(
        {
            "masked_id": 1,
            "AGE": "bad_value",
            "Acute bronchitis": "1",
            "Acute kidney failure": "0",
            "Xerosis cutis": "1",
        }
    )
    assert "AGE" in v.errors


def test_missing_column_detected():
    """A column defined in the DD but absent from the document is reported."""
    v = _make_validator_from_dd(FAILING_DD)
    # Submit a row missing 'AGE'
    v.validate({"masked_id": 1})
    assert "AGE" in v.errors
    assert any("missing" in msg for msg in v.errors["AGE"])


def test_undefined_column_detected():
    """A column present in the document but absent from the DD is reported."""
    v = _make_validator_from_dd(FAILING_DD)
    v.validate(
        {
            "masked_id": 1,
            "AGE": "one",
            "Acute bronchitis": "1",
            "Acute kidney failure": "0",
            "Xerosis cutis": "1",
            "not_in_dd": "surprise",
        }
    )
    assert "not_in_dd" in v.errors
    assert any("not defined" in msg for msg in v.errors["not_in_dd"])


def test_column_check_runs_only_once():
    """Column presence check fires on the first validate call only."""
    v = _make_validator_from_dd(FAILING_DD)
    v.validate({"masked_id": 1})  # first call — missing columns reported
    assert "AGE" in v.errors
    v.validate({"masked_id": 2})  # second call — column check already ran
    assert "AGE" not in v.errors



# prepare_and_run_datafile_validation integration tests

def test_integration_failing_files_writes_output():
    """Running validation on the failing example files produces a non-empty output CSV."""
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        out_path = tmp.name
    try:
        prepare_and_run_datafile_validation(FAILING_DATAFILE, FAILING_DD, out_path)
        with open(out_path, newline="") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) > 0
        # All 'allowed' failures for the same field should be collapsed into one row
        age_rows = [r for r in rows if r["FIELD"] == "AGE" and r["CHECK"] == "allowed"]
        assert len(age_rows) == 1
        assert "Selection of unallowed values:" in age_rows[0]["DESCRIPTION"]
        assert age_rows[0]["DESCRIPTION"].endswith(", ...")
    finally:
        os.unlink(out_path)


def test_empty_dd_raises():
    """An empty data dictionary file raises ValueError."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as dd_f:
        dd_f.write("")  # empty file
        dd_path = dd_f.name
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as out_f:
        out_path = out_f.name
    try:
        with pytest.raises(ValueError, match="empty"):
            prepare_and_run_datafile_validation(FAILING_DATAFILE, dd_path, out_path)
    finally:
        os.unlink(dd_path)
        os.unlink(out_path)


def test_dd_with_no_variable_names_raises():
    """A DD file whose rows all lack variable_name produces an empty schema and raises ValueError."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, newline=""
    ) as dd_f:
        writer = csv.DictWriter(dd_f, fieldnames=["variable_name", "data_type"])
        writer.writeheader()
        writer.writerow({"variable_name": "", "data_type": "string"})
        dd_path = dd_f.name
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as out_f:
        out_path = out_f.name
    try:
        with pytest.raises(ValueError, match="schema"):
            prepare_and_run_datafile_validation(FAILING_DATAFILE, dd_path, out_path)
    finally:
        os.unlink(dd_path)
        os.unlink(out_path)


def test_empty_datafile_raises():
    """An empty data file raises ValueError."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, newline=""
    ) as df_f:
        df_f.write("")
        df_path = df_f.name
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as out_f:
        out_path = out_f.name
    try:
        with pytest.raises(ValueError, match="empty"):
            prepare_and_run_datafile_validation(df_path, FAILING_DD, out_path)
    finally:
        os.unlink(df_path)
        os.unlink(out_path)
