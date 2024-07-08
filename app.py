"""Scrape fed rate"""

# os import
import os

# package import
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
from boto.s3.connection import S3Connection
from boto.s3.key import Key

# function import
from table_build import table_constructor


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

# Fed URL
URL = "https://www.federalreserve.gov/releases/h15/"


# request the html from the website
result = requests.get(URL, timeout=30)
# use Beautiful Soup to parse the HTML
doc = BeautifulSoup(result.text, "html.parser")
# find all of the table rows in the parsed HTML document
html_data = doc.find(id="h15table")
table_data = html_data.findChildren("tr")

# call our custom function to constuct a DataFrame
table_df = table_constructor(table_data)
# conver DataFrame to CSV
table_df.to_csv("data.csv", index=False)

# call funtion to send the CSV to S3 bucket
k.set_contents_from_filename("./data.csv")
