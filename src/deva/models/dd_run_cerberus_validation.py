import argparse

from src.deva.models.cerberus_validation.dd_validation import prepare_and_run_data_dictionary_validation


def main():
    parser = argparse.ArgumentParser(description="Run Cerberus validation on a document against a schema.")
    parser.add_argument("tgt_schema", help="Name of the schema file to validate the csv against. Schema files should be located in src/validator/resources/schemas.")
    parser.add_argument(
        "data_dictionary_path", help="Path to the csv file to be validated."
    )
    parser.add_argument(
        "output_csv_path", help="Path to write the validation results CSV file."
    )
    args = parser.parse_args()

    prepare_and_run_data_dictionary_validation(args.data_dictionary_path, args.tgt_schema, args.output_csv_path)

if __name__ == "__main__":
    main()
