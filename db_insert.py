"""Insert data into Postgres db"""

# os import
import os

# package import
import psycopg2
import pandas as pd

from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# secure variables
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_port = os.getenv("DB_PORT")

connection_string = f"postgresql://{db_user}:{db_password}@database:{db_port}/{db_user}"
db = create_engine(connection_string)
conn = db.connect()

connection = psycopg2.connect(
    f"dbname=postgres user={db_user} host=database password={db_password} port={db_port}"
)
cursor = connection.cursor()


def insert_scrape():
    """Takes scraped csv and inserts it into the scrape table."""
    # read csv and convert to df
    data = pd.read_csv("./scrape/scrape.csv", index_col=False, header=0, delimiter=",")
    # takes df and writes it to a database table
    # if data exists replace
    data.to_sql("scrape", con=conn, if_exists="append", index=False)


insert_scrape()
