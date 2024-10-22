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

dataframe_table_columns = {
    "federal_eff_funds": ["date", "rate"],
    "commercial_paper_nonfinancial": ["date", "one_month", "two_month", "three_month"],
    "commercial_paper_financial": ["date", "one_month", "two_month", "three_month"],
    "bank_prime_loan": ["date", "rate"],
    "discount_window_primary_credit": ["date", "rate"],
    "us_gov_securities_tresury_bills": [
        "date",
        "four_week",
        "three_month",
        "six_month",
        "one_year",
    ],
    "maturities_nominal_9": [
        "date",
        "one_month",
        "two_month",
        "three_month",
        "six_month",
        "one_year",
        "two_year",
        "three_year",
        "five_year",
        "seven_year",
        "ten_year",
        "twenty_year",
        "thirty_year",
    ],
    "maturities_inflation_indexed": [
        "date",
        "five_year",
        "seven_year",
        "ten_year",
        "twenty_year",
        "thirty_year",
    ],
    "us_gov_securities_tresury_bills": ["date", "one_month", "long_term_average"],
}


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
    root = "download"

    # walk the path to get the directory and files
    for subdir, dirs, files in os.walk(root):
        for file in files:

            # skip the placeholder file
            if file == ".gitkeep":
                continue
            else:
                # read csv's
                data = pd.read_csv(
                    f"./{subdir}/{file}",
                    index_col=False,
                    header=1,
                    delimiter=",",
                )

                # format dataframe to have matching columns to table columns
                # data_formated = data.set_axis(
                #     dataframe_table_columns[directory], axis=1
                # )
                # print(data_formated)

                print(subdir.split("/")[-1])

                # # upload csv
                # data.to_sql(
                #     name=directory,
                #     con=conn,
                #     if_exists="append",
                #     index=False,
                #     method=postgres_do_nothing,
                # ),


insert_download()

# close connections
cursor.close()
connection.close()
