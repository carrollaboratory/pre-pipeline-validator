import csv
from cerberus import Validator, DocumentError

from pre_pipeline_validator import s3_reader


def csv_to_dicts_chunked(
    filepath,
    chunksize=1000,
    aws_access_key_id=None,
    aws_secret_access_key=None,
    aws_session_token=None,
):
    """
    Reads a CSV file in chunks and yields lists of row dicts.
    Empty strings are normalized to None.
    """

    if filepath.startswith("s3://"):
        f = s3_reader(
            filepath, aws_access_key_id, aws_secret_access_key, aws_session_token
        )
    else:
        f = open(filepath, newline="")

    try:
        with f:
            reader = csv.DictReader(f)
            chunk = []
            for row in reader:
                chunk.append({k: (v if v != "" else None) for k, v in row.items()})
                if len(chunk) == chunksize:
                    yield chunk
                    chunk = []
            if chunk:
                yield chunk
    except csv.Error as e:
        raise ValueError(f"CSV parsing error on line {reader.line_num}: {e}") from e


# Maps Cerberus rule names to output subcategories.
RULE_SUBCATEGORY_MAP = {
    "type": "Type",
    "regex": "Format",
    "allowed": "Value",
    "min": "Range",
    "max": "Range",
    "min_length": "Range",
    "max_length": "Range",
    "required": "Completeness",
    "empty": "Completeness",
    "nullable": "Completeness",
    "check_with": "Value",
}


def run_cerberus_validation(
    schema, src_file, validator_class=Validator, allow_unknown=False
):
    """
    Runs validation using a specified Cerberus Validator class.
    Returns the validator object so callers can access errors and document_error_tree.
    """
    v = validator_class(schema, allow_unknown=allow_unknown)
    try:
        v.validate(src_file)
    except DocumentError:
        pass
    return v
