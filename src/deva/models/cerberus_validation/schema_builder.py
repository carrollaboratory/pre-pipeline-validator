
# Maps data dictionary data_type values to Cerberus type strings.
TYPE_MAP = {
    "string": "string",
    "integer": "integer",
    "float": "float",
    "boolean": "boolean",
    "date": "string", # TODO: Add a regex date format
}


def csv_to_cerberus_schema(dd_rows):
    """
    Converts a list of data dictionary row dicts into a Cerberus-compatible schema./

    """
    schema = {}
    for row in dd_rows:
        field_name = row.get("variable_name")
        if not field_name:
            continue

        rules = {}

        # Map data_type to Cerberus type
        data_type = row.get("data_type")
        if data_type:
            cerberus_type = TYPE_MAP.get(data_type.lower())
            if cerberus_type:
                rules["type"] = cerberus_type

        # required
        required_val = row.get("required")
        if required_val is not None:
            rules["required"] = str(required_val).upper() in ("TRUE", "YES", "1")
        else:
            rules["required"] = False

        # min / max — only meaningful for numeric types
        if rules.get("type") in ("integer", "float"):
            min_val = row.get("min")
            if min_val is not None:
                rules["min"] = int(min_val) if rules["type"] == "integer" else float(min_val)
            max_val = row.get("max")
            if max_val is not None:
                rules["max"] = int(max_val) if rules["type"] == "integer" else float(max_val)

        # enumerations — semicolon-separated list of allowed values
        enumerations = row.get("enumerations")
        if enumerations:
            rules["allowed"] = [e.strip() for e in enumerations.split(";")]

        # Allow null if the field is not required
        rules["nullable"] = not rules["required"]

        schema[field_name] = rules

    return schema
