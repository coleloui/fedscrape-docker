"""Script to upload data to S3 Bucket"""

# os import
import os

# package import
from dotenv import load_dotenv
from boto.s3.connection import S3Connection
from boto.s3.key import Key

load_dotenv()

# secure variables
aws_key = os.getenv("AWS_KEY")
aws_secret = os.getenv("AWS_SECRET")
s3bucket = os.getenv("S3_BUCKET")

# aws connection
aws_connection = S3Connection(aws_key, aws_secret)
bucket = aws_connection.get_bucket(s3bucket)
k = Key(bucket)
k.key = "data"


def upload_download():
    """upload the download directory and all included directories"""
    for root, dirs, files in os.walk("download"):
        print(root, dirs, files)
        for file in files:
            if file == ".gitkeep":
                continue
        #     k.set_contents_from_filename(os.path.join(root, file))


def upload_scrape():
    """upload scraped csv"""
    # call funtion to send the CSV to S3 bucket
    k.set_contents_from_filename("./scrape/scrape.csv")
