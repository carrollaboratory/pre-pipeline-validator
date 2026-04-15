import csv

class ValidationResult:
    """
    Represents the result of a single validation check.
    """
    def __init__(self, status, file, table, field, check, category, subcategory, level, notes, description, percent_records):
        self.status = status
        self.file = file
        self.table = table
        self.field = field
        self.check = check
        self.category = category
        self.subcategory = subcategory
        self.level = level
        self.notes = notes
        self.description = description
        self.percent_records = percent_records

    def to_dict(self):
        """Converts the object to a dictionary."""
        return {
            "STATUS": self.status,
            "FILE": self.file,
            "TABLE": self.table,
            "FIELD": self.field,
            "CHECK": self.check,
            "CATEGORY": self.category,
            "SUBCATEGORY": self.subcategory,
            "LEVEL": self.level,
            "NOTES": self.notes,
            "DESCRIPTION": self.description,
            "% RECORDS": self.percent_records,
        }


def write_validation_results_to_csv(results, output_path):
    """
    Writes a list of ValidationResult objects to a CSV file.
    """
    if not results:
        return

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].to_dict().keys())
        writer.writeheader()
        for result in results:
            writer.writerow(result.to_dict())
