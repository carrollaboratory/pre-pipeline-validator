from cerberus import Validator
from pathlib import Path
import csv

from src.deva.models.cerberus_validation import csv_to_dicts_chunked, run_cerberus_validation, RULE_SUBCATEGORY_MAP
from src.deva.models.validation_result import ValidationResult, write_validation_results_to_csv
from src.deva.models.cerberus_validation.schema_builder import csv_to_cerberus_schema, build_field_type_map


class DataFileValidator(Validator):
    def __init__(self, *args, **kwargs):
        self.expected_fields = kwargs.pop("expected_fields", set())
        # Handle undefined columns ourselves so the message is consistent with
        # the "missing" message; suppress Cerberus's generic "unknown field" error.
        kwargs["allow_unknown"] = True
        super(DataFileValidator, self).__init__(*args, **kwargs)
        self._column_checked = False

    def validate(self, document, *args, **kwargs):
        super(DataFileValidator, self).validate(document, *args, **kwargs)
        if not self._column_checked:
            doc_fields = set(document.keys())
            missing_fields = self.expected_fields - doc_fields
            undefined_fields = doc_fields - self.expected_fields

            for field in missing_fields:
                self._error(
                    field, f"Column {field} is missing from the data file but is defined in the data dictionary."
                )
            for field in undefined_fields:
                self._error(
                    field, f"Column {field} is present in the data file but not defined in the data dictionary."
                )
            self._column_checked = True

        return not bool(self._errors)


def prepare_and_run_datafile_validation(
    datafile_path,
    data_dictionary_path,
    output_csv_path,
    chunksize=1000,
    aws_access_key_id=None,
    aws_secret_access_key=None,
    aws_session_token=None,
):
    # Read the data dictionary to build the schema and get expected fields
    try:
        with open(data_dictionary_path, "r", newline="") as f:
            dd_rows = list(csv.DictReader(f))
    except (IOError, csv.Error) as e:
        raise ValueError(f"Error reading data dictionary: {e}") from e

    if not dd_rows:
        raise ValueError(f"Data dictionary '{data_dictionary_path}' is empty.")

    schema = csv_to_cerberus_schema(dd_rows)
    field_type_map = build_field_type_map(dd_rows)
    if not schema:
        raise ValueError(
            f"No valid schema could be built from '{data_dictionary_path}'. "
            "Ensure the file has a 'variable_name' column with at least one non-empty value."
        )

    dd_fields = {row["variable_name"] for row in dd_rows if row.get("variable_name")}
    validator = DataFileValidator(schema, expected_fields=dd_fields)

    # Load and format the source data file
    formatted_source_data = csv_to_dicts_chunked(
        datafile_path,
        chunksize,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
    )

    error_aggregator = {}
    total_rows = 0
    row_num = 2
    for chunk in formatted_source_data:
        for row in chunk:
            total_rows += 1
            # Coerce numeric fields to their declared Python type immediately
            # after reading so the row dict has correct types before validation.
            for field, cast in field_type_map.items():
                if row.get(field) is not None:
                    try:
                        row[field] = cast(row[field])
                    except (ValueError, TypeError):
                        pass  # leave as-is; Cerberus will report the type error
            validator.validate(row)
            if validator.errors:
                for field, error_list in validator.errors.items():
                    error = error_list[0]
                    field_node = validator.document_error_tree[field] if field in validator.document_error_tree else None
                    field_ve_list = field_node.errors if field_node else []
                    ve = field_ve_list[0] if field_ve_list else None
                    rule = ve.rule if ve else "unknown"
                    # Group all 'allowed' failures for the same field into one entry
                    # so every unique bad value doesn't produce its own output row.
                    if rule == "allowed":
                        key = (field, "allowed")
                        bad_value = row.get(field)
                        if key not in error_aggregator:
                            error_aggregator[key] = {
                                "field": field,
                                "error": error,
                                "rule": rule,
                                "bad_values": [],
                                "rows": [],
                            }
                        if bad_value not in error_aggregator[key]["bad_values"]:
                            error_aggregator[key]["bad_values"].append(bad_value)
                    else:
                        key = (field, error)
                        if key not in error_aggregator:
                            error_aggregator[key] = {
                                "field": field,
                                "error": error,
                                "rule": rule,
                                "bad_values": [],
                                "rows": [],
                            }
                    error_aggregator[key]["rows"].append(row_num)
            row_num += 1

    if total_rows == 0:
        raise ValueError(f"Data file '{datafile_path}' is empty.")

    if not error_aggregator:
        print("Validation successful: The document is valid.")
        return

    validation_results = []
    for entry in error_aggregator.values():
        pct = f"{len(entry['rows']) / total_rows:.2%}" if total_rows > 0 else "N/A"
        
        rule = entry.get("rule", "unknown")
        if "missing" in entry["error"]:
            subcategory = "Missing Column"
            level = "TABLE"
            check = "column_present"
        elif "not defined" in entry["error"]:
            subcategory = "Undefined Column"
            level = "TABLE"
            check = "column_defined"
        else:
            subcategory = RULE_SUBCATEGORY_MAP.get(rule, "Value")
            level = "FIELD"
            check = rule

        result = ValidationResult(
            status="Fail",
            file=Path(datafile_path).stem,
            table=Path(data_dictionary_path).stem,
            field=entry["field"],
            check=check,
            category="Conformity",
            subcategory=subcategory,
            level=level,
            notes=None,
            description=(
                "Selection of unallowed values: "
                + ", ".join(str(v) for v in entry["bad_values"][:5])
                + ", ..."
                if entry.get("bad_values")
                else entry["error"]
            ),
            percent_records=pct,
        )
        validation_results.append(result)

    write_validation_results_to_csv(validation_results, output_csv_path)
    print(f"Validation failed. Results written to {output_csv_path}")
