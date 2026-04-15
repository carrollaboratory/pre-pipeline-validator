import argparse

from pre_pipeline_validator.models.cerberus_validation.cerb_df_validation import (
    prepare_and_run_datafile_validation,
)


def main():
    parser = argparse.ArgumentParser(
        description="Run Cerberus validation on a data file against its data dictionary schema."
    )
    parser.add_argument("data_dictionary_path", help="Path to the data dictionary csv file. Expected to be in a schema defined format.")
    parser.add_argument(
        "datafile_path", help="Path to the csv data file to be validated."
    )
    parser.add_argument(
        "output_csv_path", help="Path to write the validation results CSV file."
    )
    parser.add_argument(
        "--aws-access-key-id",
        help="AWS access key ID for reading/writing from S3 paths.",
    )
    parser.add_argument(
        "--aws-secret-access-key",
        help="AWS secret access key for reading/writing from S3 paths.",
    )
    parser.add_argument(
        "--aws-session-token",
        help="AWS session token for reading/writing from S3 paths, if using temporary credentials.",
    )
    args = parser.parse_args()

    prepare_and_run_datafile_validation(
        args.datafile_path,
        args.data_dictionary_path,
        args.output_csv_path,
        args.aws_access_key_id,
        args.aws_secret_access_key,
        args.aws_session_token,
    )

if __name__ == "__main__":
    main()
