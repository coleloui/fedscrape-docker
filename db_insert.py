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

# connect to postgres using sqlalchemy
connection_string = f"postgresql://{db_user}:{db_password}@database:{db_port}/{db_user}"
db = create_engine(connection_string)
conn = db.connect()

# connect to postgres using psycopg2
connection = psycopg2.connect(
    f"dbname=postgres user={db_user} host=database password={db_password} port={db_port}"
)
# create a curosor for queries
cursor = connection.cursor()


def postgres_do_nothing(table, conn, keys, data_iter):
    """If data exists skip"""
    from sqlalchemy.dialects.postgresql import insert

    data = [dict(zip(keys, row)) for row in data_iter]

    insert_statement = insert(table.table).values(data)
    upsert_statement = insert_statement.on_conflict_do_nothing()
    conn.execute(upsert_statement)


# insert scrap data into the scrap table
def insert_scrape():
    """Takes scraped csv and inserts it into the scrape table."""
    # read csv and convert to df
    data = pd.read_csv("./scrape/scrape.csv", index_col=False, header=0, delimiter=",")
    # takes df and writes it to a database table
    data.to_sql(
        name="scrape",
        con=conn,
        if_exists="append",
        index=False,
        method=postgres_do_nothing,
    )


def insert_download():
    """Takes downloaded data and inserts it into the specific tables"""
    # file path for download
    root = "./download"

    # walk the path to get the directory and files
    for subdir, dirs, files in os.walk(root):
        for file in files:
            # skip the placeholder file
            if file == ".gitkeep":
                continue
            else:
                # read csv's
                data = pd.read_csv(
                    f"./{root}/{subdir}/{file}",
                    index_col=False,
                    header=6,
                    delimiter=",",
                )
                # upload csv
                data.to_sql(
                    name=subdir,
                    con=conn,
                    if_exists="append",
                    index=False,
                    method=postgres_do_nothing,
                )


insert_download()

# close connections
cursor.close()
connection.close()
