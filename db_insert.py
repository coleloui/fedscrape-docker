"""Insert data into Postgres db"""

# os import
import os

# package import
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# secure variables
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_port = os.getenv("DB_PORT")

connection = psycopg2.connect(
    f"dbname=postgres user={db_user} host=database password={db_password} port={db_port}"
)

cursor = connection.cursor()


def insert_scrape():
    """Takes scraped csv and inserts it into the scrape table."""
    # read csv and convert to df
    # data = pd.read_csv("./scrape/scrape.csv", index_col=False, header=0, delimiter=",")
    # takes df and writes it to a database table
    # if data exists replace
    # data.to_sql("scrape", con=engine, if_exists="append")

    # df = pd.read_sql("select * from scrape", con=engine)
    cursor.execute(
        """
        CREATE TEMP TABLE tmp_table
        ON COMMIT DROP
        AS
        SELECT *
        FROM select
        WITH NO DATA;

        COPY tmp_table FROM './scrape/scrape.csv';
        
        """
    )


insert_scrape()
