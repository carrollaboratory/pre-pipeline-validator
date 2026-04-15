import s3fs
from io import TextIOWrapper
from botocore.exceptions import ClientError, NoCredentialsError

def s3_reader(
    filepath,
    aws_access_key_id=None,
    aws_secret_access_key=None,
    aws_session_token=None,
):
    """
    Initializes an S3 file system object and opens a file stream.
    Handles authentication and file not found errors.
    """
    try:
        s3 = s3fs.S3FileSystem(
            key=aws_access_key_id,
            secret=aws_secret_access_key,
            token=aws_session_token,
        )
        f = s3.open(filepath, "rb")
    except (ClientError, NoCredentialsError) as e:
        raise ValueError(f"S3 authentication failed: {e}")
    except FileNotFoundError:
        raise ValueError(f"S3 file not found at path: {filepath}")

    return TextIOWrapper(f, encoding="utf-8")
