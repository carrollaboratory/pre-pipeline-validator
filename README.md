# pre-pipeline-validator

**pre-pipeline-validator(PPV)** — a command-line tool for validating data dictionaries and data files using schema-based rules. Validation results are written to a CSV report detailing every failure with its status, category, level, and description.

---

## Requirements

- Python >= 3.10

Dependencies (installed automatically):
- [`cerberus`](https://docs.python-cerberus.org/) — schema validation engine
- [`s3fs`](https://s3fs.readthedocs.io/) — S3 path support

---

## Installation

It is recommended to use a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the package from GitHub:

```bash
pip install git+https://github.com/brendagutman/validator.git
```

Or install locally from source:

```bash
pip install .
```

---

## Commands

### `validate_dd` — Validate a Data Dictionary

Validates a data dictionary CSV against a named schema. Each row in the data dictionary (representing one variable) is checked for correct formatting, required fields, valid data types, and numeric constraint usage.

```bash
validate_dd <tgt_schema> <data_dictionary_path> <output_csv_path> [options]
```

#### Arguments

| Argument | Required | Description |
|---|---|---|
| `tgt_schema` | Yes | Name of the schema to validate against (e.g. `example_data_dictionary`). Schema files are located in `src/deva/schemas/`. |
| `data_dictionary_path` | Yes | Path to the data dictionary CSV file to validate. Can be a local path or an S3 URI (`s3://...`). |
| `output_csv_path` | Yes | Path to write the validation results CSV. The file will be created or overwritten. |
| `--aws-access-key-id` | No | AWS access key ID, required when reading/writing S3 paths. |
| `--aws-secret-access-key` | No | AWS secret access key, required when reading/writing S3 paths. |
| `--aws-session-token` | No | AWS session token for temporary credentials when reading/writing S3 paths. |

#### Examples

```bash
# Validate a passing data dictionary
validate_dd example_data_dictionary src/resources/examples/passing_dd.csv src/resources/output/dd_validation_example_response.csv

# Validate a failing data dictionary
validate_dd example_data_dictionary src/resources/examples/failing_dd.csv src/resources/output/dd_validation_example_response.csv
```

---

### `validate_df` — Validate a Data File

Validates a data file CSV against a data dictionary. The schema is built dynamically from the data dictionary. Checks cover column presence, data types, allowed values, numeric ranges, and required field completeness. Results are aggregated across rows and include a `% RECORDS` column.

```bash
validate_df <data_dictionary_path> <datafile_path> <output_csv_path> [options]
```

> **Note:** Data files should not be validated against a failing data dictionary.

#### Arguments

| Argument | Required | Description |
|---|---|---|
| `data_dictionary_path` | Yes | Path to the data dictionary CSV file that defines the expected schema. Can be a local path or an S3 URI (`s3://...`). |
| `datafile_path` | Yes | Path to the data file CSV to validate. Can be a local path or an S3 URI (`s3://...`). |
| `output_csv_path` | Yes | Path to write the validation results CSV. The file will be created or overwritten. |
| `--aws-access-key-id` | No | AWS access key ID, required when reading/writing S3 paths. |
| `--aws-secret-access-key` | No | AWS secret access key, required when reading/writing S3 paths. |
| `--aws-session-token` | No | AWS session token for temporary credentials when reading/writing S3 paths. |

#### Examples

```bash
# Validate a passing data file
validate_df src/resources/examples/passing_dd.csv src/resources/examples/passing_datafile.csv src/resources/output/df_validation_example_response.csv

# Validate a failing data file
validate_df src/resources/examples/passing_dd.csv src/resources/examples/failing_datafile.csv src/resources/output/df_validation_example_response.csv
```

---

## Validation Checks

### Data Dictionary Checks (`validate_dd`)

Each row of the data dictionary is validated against the named schema. All failures are reported at the `FIELD` level with category `Conformity`.

| Check | Subcategory | Rule | Description |
|---|---|---|---|
| `type` | Type | `type` | `variable_name` must be a string. `data_type` must be a string. Other typed fields must match their declared Cerberus type. |
| `required` | Completeness | `required` | `variable_name` and `data_type` are required and must be non-empty. |
| `empty` | Completeness | `empty` | `variable_name` must not be an empty string. |
| `regex` | Format | `regex` | `variable_name` must match `^[A-Za-z_][A-Za-z0-9_]*$` (start with a letter or underscore; contain only letters, digits, or underscores). |
| `allowed` | Value | `allowed` | `data_type` must be one of: `string`, `integer`, `float`, `boolean`, `date`. `required` field (if present) must be `yes`, `no`, or empty. |
| `check_with` | Value | `numeric_constraints` | `min` and `max` values are only allowed when `data_type` is `integer` or `float`. |

### Data File Checks (`validate_df`)

The schema is built dynamically from the data dictionary. Failures are reported at `FIELD` level (per-value checks) or `TABLE` level (column presence checks), all with category `Conformity`. Results are aggregated across all rows and include a `% RECORDS` column.

| Check | Subcategory | Level | Rule | Description |
|---|---|---|---|---|
| `column_present` | Missing Column | TABLE | structural | A column defined in the data dictionary is absent from the data file. |
| `column_defined` | Undefined Column | TABLE | structural | A column in the data file is not defined in the data dictionary. |
| `type` | Type | FIELD | `type` | A field value does not match the `data_type` declared in the data dictionary (`string`, `integer`, `float`, `boolean`). |
| `allowed` | Value | FIELD | `allowed` | A field value is not in the enumerated list defined in the data dictionary `enumerations` column. Unique bad values are aggregated into a single result row per field. |
| `min` / `max` | Range | FIELD | `min` / `max` | A numeric field value falls outside the `min` or `max` range declared in the data dictionary. |
| `nullable` | Completeness | FIELD | `nullable` | A field marked `required: yes` in the data dictionary is null or empty. |

#### Notes
- `date` fields are currently validated as `string` type. Date format regex validation is not yet implemented.
- `min`/`max` constraints are only applied to `integer` and `float` fields.
- Non-numeric values in numeric fields are left as-is for Cerberus to report as a `type` error.

---

## Cerberus Built-in Rules Reference

All rules below are available out of the box in [Cerberus](https://docs.python-cerberus.org/validation-rules.html). Rows marked **Used** are currently wired into this project's schemas or schema builder.

| Rule | Used | Description |
|---|---|---|
| `allowed` | Yes | Value must be one of a defined list of allowed values. For iterables, all members must be in the list. |
| `allof` | No | Validates if **all** of the provided rule sets validate the field. |
| `anyof` | No | Validates if **any** of the provided rule sets validate the field. |
| `check_with` | Yes | Calls a custom function or validator method to validate the field value. Used for the `numeric_constraints` check. |
| `contains` | No | Validates that a container value contains all of the specified items. |
| `dependencies` | No | Field is only required if one or more other specified fields (and optionally their values) are present. |
| `empty` | Yes | If `False`, validation fails for empty iterables (e.g. empty strings). |
| `excludes` | No | Field must not coexist with one or more other specified fields. |
| `forbidden` | No | Opposite of `allowed` — validation fails if the value is in the forbidden list. |
| `items` | No | Validates each item in a fixed-length list against a corresponding rule. |
| `keysrules` | No | Applies a set of rules to all keys of a mapping (dict). |
| `min` / `max` | Yes | Minimum and maximum allowed value for any comparable type (integer, float, date, etc.). |
| `minlength` / `maxlength` | No | Minimum and maximum length for sized types (`string`, `list`, etc.) that implement `__len__`. |
| `noneof` | No | Validates if **none** of the provided rule sets validate the field. |
| `nullable` | Yes | If `True`, allows `None` as a valid value. Defaults to `False`. |
| `oneof` | No | Validates if **exactly one** of the provided rule sets validates the field. |
| `readonly` | No | If `True`, validation fails if the field is present in the document (useful for read-only/generated fields). |
| `regex` | Yes | Value must match the provided regular expression. Only tested on string values. |
| `require_all` | No | When used with a nested `schema` rule, marks all fields in the sub-document as required. |
| `required` | Yes | If `True`, the field must be present in the document. |
| `schema` (dict) | No | Validates a mapping value against a nested schema definition. |
| `schema` (list) | No | Validates each item in a list against the provided rules. |
| `type` | Yes | Restricts the field value to one or more data types (`string`, `integer`, `float`, `boolean`, `date`, `datetime`, `list`, `dict`, `number`, `binary`, `set`). |
| `valuesrules` | No | Applies a set of rules to all values of a mapping (dict). |
