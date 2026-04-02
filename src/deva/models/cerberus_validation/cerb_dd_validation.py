from cerberus import Validator
from pathlib import Path

from src.deva.models.cerberus_validation import csv_to_dicts_chunked, run_cerberus_validation, RULE_SUBCATEGORY_MAP
from src.deva.models.validation_result import ValidationResult, write_validation_results_to_csv


class DataDictionaryValidator(Validator):
    def _check_with_numeric_constraints(self, field, value):
        """
        Checks that 'min' and 'max' are only present for numeric data types.
        """
        if value is None:
            return

        dt = self.document.get("data_type")

        if dt not in {"integer", "float"}:
            self._error(
                field,
                "min/max is only allowed for numeric data types (integer, float).",
            )

def prepare_and_run_data_dictionary_validation(data_dictionary_path, tgt_schema, output_csv_path, chunksize=1000, aws_access_key_id=None, aws_secret_access_key=None, aws_session_token=None):
    # Load and format the source data.
    formatted_source_data = csv_to_dicts_chunked(data_dictionary_path, chunksize=chunksize, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=aws_session_token)

    # Import the specified schema module and retrieve the schema.
    try:
        schema_module = __import__(f"deva.schemas.{tgt_schema}", fromlist=["schema"])
        schema = getattr(schema_module, "schema")
    except (ImportError, AttributeError):
        raise ValueError(f"Schema '{tgt_schema}' not found or is invalid.")

    validator_class = (
        DataDictionaryValidator if "data_dictionary" in tgt_schema else Validator
    )

    validation_results = []
    row_num = 2
    for chunk in formatted_source_data:
        for row in chunk:
            v = run_cerberus_validation(schema, row, validator_class=validator_class)
            if v.errors:
                for field, error_list in v.errors.items():
                    field_node = v.document_error_tree[field]
                    field_ve_list = field_node.errors if field_node else []
                    for idx, error in enumerate(error_list):
                        ve = field_ve_list[idx] if idx < len(field_ve_list) else None
                        rule = ve.rule if ve else "unknown"
                        constraint = ve.constraint if ve else None
                        subcategory = RULE_SUBCATEGORY_MAP.get(rule, "Value")
                        constraint_info = f" (constraint: {constraint})" if constraint is not None else ""
                        result = ValidationResult(
                            status="Fail",
                            file=Path(data_dictionary_path).stem,
                            table=tgt_schema,
                            field=field,
                            check=rule,
                            category="Conformity",
                            subcategory=subcategory,
                            level="FIELD",
                            notes=None,
                            description=f"Value '{row.get(field)}' in row {row_num} {error}{constraint_info}",
                            percent_records=None,
                        )
                        validation_results.append(result)
            row_num += 1

    if not validation_results:
        print("Validation successful: The document is valid.")
    else:
        write_validation_results_to_csv(validation_results, output_csv_path)
        print(f"Validation failed. Results written to {output_csv_path}")
