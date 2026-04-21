from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class CheckMeta:
    """Metadata for a single validation check.
    
    """
    check: str
    category: str
    subcategory: str
    status: str = "Fail"   # "Fail" or "Warn"
    level: str = "FIELD"   # "FIELD" or "TABLE"
    description: str = ""  # Default description; use {field}, {value}, {row}, {error} as placeholders


class CheckRegistry:
    """Maps rule/check names to CheckMeta.

    """

    _defaults: Dict[str, "CheckMeta"] = {
        "type": CheckMeta(
            check="data type",
            category="Cerberus",
            subcategory="Type",
            status="Fail",
            level="FIELD",
            description="Value '{value}' (type: {value_type}) in row {row} failed data type check: {error}",
        ),
        "regex": CheckMeta(
            check="regex",
            category="Cerberus",
            subcategory="Format",
            status="Fail",
            level="FIELD",
            description="Value '{value}' in row {row} does not match required format: {error}",
        ),
        "allowed": CheckMeta(
            check="allowed",
            category="Cerberus",
            subcategory="Value",
            status="Fail",
            level="FIELD",
            description="Selection of unallowed values: {value}",
        ),
        "min": CheckMeta(
            check="minimum",
            category="Cerberus",
            subcategory="Range",
            status="Fail",
            level="FIELD",
            description="Value '{value}' in row {row} is below the minimum: {error}",
        ),
        "max": CheckMeta(
            check="maximum",
            category="Cerberus",
            subcategory="Range",
            status="Fail",
            level="FIELD",
            description="Value '{value}' in row {row} exceeds the maximum: {error}",
        ),
        "min_length": CheckMeta(
            check="min_length",
            category="Cerberus",
            subcategory="Range",
            status="Fail",
            level="FIELD",
            description="Value '{value}' in row {row} is shorter than the minimum length: {error}",
        ),
        "max_length": CheckMeta(
            check="max_length",
            category="Cerberus",
            subcategory="Range",
            status="Fail",
            level="FIELD",
            description="Value '{value}' in row {row} exceeds the maximum length: {error}",
        ),
        "required": CheckMeta(
            check="required",
            category="Cerberus",
            subcategory="Completeness",
            status="Fail",
            level="FIELD",
            description="Required field '{field}' is missing in row {row}: {error}",
        ),
        "empty": CheckMeta(
            check="empty",
            category="Cerberus",
            subcategory="Completeness",
            status="Fail",
            level="FIELD",
            description="Field '{field}' must not be empty in row {row}: {error}",
        ),
        "nullable": CheckMeta(
            check="nullable",
            category="Cerberus",
            subcategory="Completeness",
            status="Fail",
            level="FIELD",
            description="Field '{field}' is null or empty in row {row} but is required: {error}",
        ),
        "check_with": CheckMeta(
            check="check_with",
            category="Cerberus",
            subcategory="Value",
            status="Fail",
            level="FIELD",
            description="Value '{value}' in row {row} failed custom check: {error}",
        ),
        "column_present": CheckMeta(
            check="column_present",
            category="Custom",
            subcategory="Missing Column",
            status="Fail",
            level="TABLE",
            description="Column '{field}' is missing from the data file but is defined in the data dictionary.",
        ),
        "column_defined": CheckMeta(
            check="column_defined",
            category="Custom",
            subcategory="Undefined Column",
            status="Fail",
            level="TABLE",
            description="Column '{field}' is present in the data file but not defined in the data dictionary.",
        ),
    }

    def __init__(self):
        self._registry: Dict[str, CheckMeta] = dict(self._defaults)

    def register(self, meta: CheckMeta) -> None:
        """Add or override a check entry."""
        self._registry[meta.check] = meta

    def get(self, rule: str, fallback_check: Optional[str] = None) -> CheckMeta:
        """Return CheckMeta for the given rule name.

        If not found, returns a default 'Fail/FIELD/Conformity/Value' entry
        using fallback_check (or rule) as the check name.
        """
        if rule in self._registry:
            return self._registry[rule]
        name = fallback_check or rule
        return CheckMeta(check=name, category="Conformity", subcategory="Value", status="Fail", level="FIELD")


# Module-level default registry — import and use directly, or instantiate your own.
DEFAULT_REGISTRY = CheckRegistry()
