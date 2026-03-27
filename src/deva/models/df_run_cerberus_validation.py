import argparse

from src.deva.models.cerberus_validation.df_validation import prepare_and_run_datafile_validation


def main():
    parser = argparse.ArgumentParser(description="Run Cerberus validation on a data file against its data dictionary schema.")
    parser.add_argument("datafile_path", help="Path to the csv data file to be validated.")
    parser.add_argument("data_dictionary_path", help="Path to the data dictionary csv file. Expected to be in a schema defined format.")
    parser.add_argument(
        "output_csv_path", help="Path to write the validation results CSV file."
    )
    args = parser.parse_args()

    prepare_and_run_datafile_validation(args.datafile_path, args.data_dictionary_path, args.output_csv_path)

if __name__ == "__main__":
    main()
