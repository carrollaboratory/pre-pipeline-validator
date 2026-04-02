import argparse

from deva.models.cerberus_validation.cerb_dd_validation import (
    prepare_and_run_data_dictionary_validation,
)


def main():
    parser = argparse.ArgumentParser(description="Run Cerberus validation on a document against a schema.")
    parser.add_argument("tgt_schema", help="Name of the schema file to validate the csv against. Schema files should be located in src/validator/resources/schemas.")
    parser.add_argument(
        "data_dictionary_path", help="Path to the csv file to be validated."
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

    prepare_and_run_data_dictionary_validation(
        args.data_dictionary_path,
        args.tgt_schema,
        args.output_csv_path,
        aws_access_key_id=args.aws_access_key_id,
        aws_secret_access_key=args.aws_secret_access_key,
        aws_session_token=args.aws_session_token,
    )

if __name__ == "__main__":
    main()
