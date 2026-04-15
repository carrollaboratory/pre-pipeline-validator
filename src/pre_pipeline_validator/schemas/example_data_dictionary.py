ALLOWED_DATA_TYPES = [
    "string",
    "integer",
    "float",
    "boolean",
    "date"
]

schema = {
    "variable_name": {
        "type": "string",
        "required": True,
        "empty": False,
        "regex": "^[A-Za-z_][A-Za-z0-9_]*$",
    },
    "description": {"type": "string", "nullable": True},
    "data_type": {"type": "string", "required": True, "allowed": ALLOWED_DATA_TYPES},
    "min": {"nullable": True, "check_with": "numeric_constraints"},
    "max": {"nullable": True, "check_with": "numeric_constraints"},
    "units": {"type": "string", "nullable": True},
    "enumerations": {"type": "string", "nullable": True},
    "comment": {"type": "string", "nullable": True},
    "required": {"type": "string", "nullable": True, "allowed": ["yes", "no", None]},
    "extra_row": {"type": "string", "nullable": True},
}
