import csv
from cerberus import Validator, DocumentError
from typing import Generator


def csv_to_dicts_chunked(filepath, chunk_size=1000) -> Generator:
    """
    Reads a CSV file in chunks and yields lists of row dicts.
    Empty strings are normalized to None.

    """
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        chunk = []
        for row in reader:
            chunk.append({k: (v if v != "" else None) for k, v in row.items()})
            if len(chunk) == chunk_size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk


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


def run_cerberus_validation(schema, src_file, validator_class=Validator):
    """
    Runs validation using a specified Cerberus Validator class.
    Returns the validator object so callers can access errors and document_error_tree.
    """
    v = validator_class(schema, allow_unknown=True)
    try:
        v.validate(src_file)
    except DocumentError:
        pass
    return v
