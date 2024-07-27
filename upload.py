"""Script to upload data to S3 Bucket"""

# os import
import os

# package import
import botocore.exceptions
from dotenv import load_dotenv
from boto3 import session

load_dotenv()

# secure variables
aws_key = os.getenv("AWS_KEY")
aws_secret = os.getenv("AWS_SECRET")
aws_region = os.getenv("AWS_REGION")
s3bucket = os.getenv("S3_BUCKET")

# aws connection
aws_session = session.Session(
    region_name=aws_region,
    aws_access_key_id=aws_key,
    aws_secret_access_key=aws_secret,
)
s3 = aws_session.resource("s3")


def test_connection():
    """This function tests our S3 connection.
    If it exists it will allow users to save files to their S3"""
    try:
        s3.meta.client.head_bucket(Bucket=s3bucket)
        return True
    except botocore.exceptions.ClientError as e:
        error_code = int(e.response["Error"]["Code"])
        if error_code == 403:
            print("Forbidden Access")
            return False
        elif error_code == 404:
            print("Bucket Doenst Exist")
            return False
        else:
            print("No Connection")
            return False


def upload_download():
    """upload the download directory and all included directories"""
    for root, dirs, files in os.walk("download"):
        for file in files:
            if file == ".gitkeep":
                continue
            else:
                current_directory = root.split("\\").pop(-1)
                s3.Object(s3bucket, f"data/{current_directory}/{file}").put(
                    Body=open(os.path.join(root, file), "rb")
                )
                print("upload complete")


def upload_scrape():
    """upload scraped csv"""
    # call funtion to send the CSV to S3 bucket
    s3.Object(s3bucket, "data/scrape/scrape.csv").put(
        Body=open("scrape/scrape.csv", "rb")
    )
    print("upload complete")
