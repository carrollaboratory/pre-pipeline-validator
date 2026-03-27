from cerberus import Validator, DocumentError
from pathlib import Path
import csv

from src.deva.models.cerberus_validation import csv_to_dicts_chunked, run_cerberus_validation, RULE_SUBCATEGORY_MAP
from src.deva.models.validation_result import ValidationResult, write_validation_results_to_csv
from src.deva.models.cerberus_validation.schema_builder import csv_to_cerberus_schema


def _build_row_description(row_nums):
    """Builds the failing rows string, truncating with '...' after 10 rows."""
    if len(row_nums) > 10:
        return "Failing rows: " + ",".join(str(r) for r in row_nums[:10]) + ",..."
    return "Failing rows: " + ",".join(str(r) for r in row_nums)


def _build_description(field, rule, constraint, row_nums):
    """Builds a description based on the failing rule."""
    rows_str = _build_row_description(row_nums)
    if rule == "min":
        return f"The minimum value for {field} is {constraint}. {rows_str}"
    elif rule == "max":
        return f"The maximum value for {field} is {constraint}. {rows_str}"
    elif rule == "type":
        return f"{field} must be of type '{constraint}'. {rows_str}"
    elif rule == "allowed":
        return f"{field} must be one of the allowed values: {constraint}. {rows_str}"
    elif rule == "regex":
        return f"{field} must match the pattern: {constraint}. {rows_str}"
    elif rule in ("required", "empty"):
        return f"{field} is required and cannot be empty. {rows_str}"
    elif rule == "nullable":
        return f"{field} cannot be null. {rows_str}"
    elif rule == "min_length":
        return f"{field} must have a minimum length of {constraint}. {rows_str}"
    elif rule == "max_length":
        return f"{field} must have a maximum length of {constraint}. {rows_str}"
    else:
        return f"{field} failed {rule} validation. {rows_str}"


def prepare_and_run_datafile_validation(datafile_path, data_dictionary_path, output_csv_path, chunk_size=1000):
    # Load and format the source data.
    formatted_source_data = csv_to_dicts_chunked(datafile_path, chunk_size=chunk_size)

    schema = csv_to_cerberus_schema(
        row for chunk in csv_to_dicts_chunked(data_dictionary_path) for row in chunk
    )

    error_aggregator = {}
    total_rows = 0
    row_num = 2 
    for chunk in formatted_source_data:
        for row in chunk:
            total_rows += 1
            v = run_cerberus_validation(schema, row, validator_class=Validator)
            if v.errors:
                for field, error_list in v.errors.items():
                    field_node = v.document_error_tree[field]
                    field_ve_list = field_node.errors if field_node else []
                    for i, error in enumerate(error_list):
                        ve = field_ve_list[i] if i < len(field_ve_list) else None
                        rule = ve.rule if ve else "unknown"
                        constraint = ve.constraint if ve else None
                        subcategory = RULE_SUBCATEGORY_MAP.get(rule, "Value")
                        key = (field, rule, str(constraint))
                        if key not in error_aggregator:
                            error_aggregator[key] = {
                                "field": field,
                                "rule": rule,
                                "constraint": constraint,
                                "subcategory": subcategory,
                                "error": error,
                                "rows": [],
                            }
                        error_aggregator[key]["rows"].append(row_num)
            row_num += 1

    if not error_aggregator:
        print("Validation successful: The document is valid.")
        return

    validation_results = []
    for entry in error_aggregator.values():
        pct = f"{len(entry['rows']) / total_rows:.2%}" if total_rows > 0 else "N/A"
        result = ValidationResult(
            status="Fail",
            file=Path(datafile_path).stem,
            table=Path(data_dictionary_path).stem,
            field=entry["field"],
            check=entry["rule"],
            category="Conformity",
            subcategory=entry["subcategory"],
            level="FIELD",
            notes=None,
            description=_build_description(entry["field"], entry["rule"], entry["constraint"], entry["rows"]),
            percent_records=pct,
        )
        validation_results.append(result)

    write_validation_results_to_csv(validation_results, output_csv_path)
    print(f"Validation failed. Results written to {output_csv_path}")
