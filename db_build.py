"""build PostgreSQL db tables"""

# os import
import os

# package import
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# secure variables
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_port = os.getenv("DB_PORT")

connection = psycopg2.connect(
    f"dbname=postgres user={db_user} host=database password={db_password} port={db_port}"
)


def build_scrape():
    """builds the scrape table in the postgres"""
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE scrape (
        id SERIAL PRIMARY KEY UNIQUE NOT NULL,
        date DATE UNIQUE NOT NULL,
        "Federal funds" VARCHAR(50) NOT NULL,
        "Commercial Paper - Nonfinancial - 1 Month" VARCHAR(50) NOT NULL,
        "Commercial Paper - Nonfinancial - 2 Month" VARCHAR(50) NOT NULL,
        "Commercial Paper - Nonfinancial - 3 Month" VARCHAR(50) NOT NULL,
        "Commercial Paper - Financial - 1 Month" VARCHAR(50) NOT NULL,
        "Commercial Paper - Financial - 2 Month" VARCHAR(50) NOT NULL,
        "Commercial Paper - Financial - 3 Month" VARCHAR(50) NOT NULL,
        "Bank prime loan" VARCHAR(50) NOT NULL,
        "Discount window primary credit" VARCHAR(50) NOT NULL,
        "U.S. gov - Bills - 4 week" VARCHAR(50) NOT NULL,
        "U.S. gov - Bills - 3 month" VARCHAR(50) NOT NULL,
        "U.S. gov - Bills - 6 month" VARCHAR(50) NOT NULL,
        "U.S. gov - Bills - 1 year" VARCHAR(50) NOT NULL,
        "U.S. gov - Maturities - Nominal 9 - 1 month" VARCHAR(50) NOT NULL,
        "U.S. gov - Maturities - Nominal 9 - 3 month" VARCHAR(50) NOT NULL,
        "U.S. gov - Maturities - Nominal 9 - 6 month" VARCHAR(50) NOT NULL,
        "U.S. gov - Maturities - Nominal 9 - 1 year" VARCHAR(50) NOT NULL,
        "U.S. gov - Maturities - Nominal 9 - 2 year" VARCHAR(50) NOT NULL,
        "U.S. gov - Maturities - Nominal 9 - 3 year" VARCHAR(50) NOT NULL,
        "U.S. gov - Maturities - Nominal 9 - 5 year" VARCHAR(50) NOT NULL,
        "U.S. gov - Maturities - Nominal 9 - 7 year" VARCHAR(50) NOT NULL,
        "U.S. gov - Maturities - Nominal 9 - 10 year" VARCHAR(50) NOT NULL,
        "U.S. gov - Maturities - Nominal 9 - 20 year" VARCHAR(50) NOT NULL,
        "U.S. gov - Maturities - Nominal 9 - 30 year" VARCHAR(50) NOT NULL,
        "U.S. gov - Maturities - Inflation indexed - 5 year" VARCHAR(50) NOT NULL,
        "U.S. gov - Maturities - Inflation indexed - 7 year" VARCHAR(50) NOT NULL,
        "U.S. gov - Maturities - Inflation indexed - 10 year" VARCHAR(50) NOT NULL,
        "U.S. gov - Maturities - Inflation indexed - 20 year" VARCHAR(50) NOT NULL,
        "U.S. gov - Maturities - Inflation indexed - 30 year" VARCHAR(50) NOT NULL,
        "U.S. gov - Inflation-indexed long-term average" VARCHAR(50) NOT NULL);"""
    )


def build_full():
    """Builds the full table range in database"""
    cursor = connection.cursor()

    cursor.execute(
        """
    CREATE TABLE federal_funds (
      id SERIAL PRIMARY KEY UNIQUE,
      date DATE UNIQUE NOT NULL,
      rate VARCHAR(50) NOT NULL);

    CREATE TABLE commercial_paper_nonfinancial (
        id SERIAL PRIMARY KEY UNIQUE,
        date DATE UNIQUE NOT NULL,
        one_month VARCHAR(50) NOT NULL,
        two_month VARCHAR(50) NOT NULL,
        three_month VARCHAR(50) NOT NULL);

    CREATE TABLE commercial_paper_financial (
        id SERIAL PRIMARY KEY UNIQUE,
        date DATE UNIQUE NOT NULL,
        one_month VARCHAR(50) NOT NULL,
        two_month VARCHAR(50) NOT NULL,
        three_month VARCHAR(50) NOT NULL);
    
    CREATE TABLE bank_prime_loan (
      id SERIAL PRIMARY KEY UNIQUE,
      date DATE UNIQUE NOT NULL,
      rate VARCHAR(50) NOT NULL);
 
    CREATE TABLE discount_window_primary_credit (
        did SERIAL PRIMARY KEY UNIQUE,
        date DATE UNIQUE NOT NULL,
        rate VARCHAR(50) NOT NULL);
    
    CREATE TABLE us_gov_securities_tresury_bills (
        id SERIAL PRIMARY KEY UNIQUE,
        date DATE UNIQUE NOT NULL,
        four_week VARCHAR(50) NOT NULL,
        three_month VARCHAR(50) NOT NULL,
        six_month VARCHAR(50) NOT NULL,
        one_year VARCHAR(50) NOT NULL);
    
    CREATE TABLE maturties_nominal_9 (
        id SERIAL PRIMARY KEY UNIQUE,
        date DATE UNIQUE NOT NULL,
        one_month VARCHAR(50) NOT NULL,
        three_month VARCHAR(50) NOT NULL,
        six_month VARCHAR(50) NOT NULL,
        one_year VARCHAR(50) NOT NULL,
        two_year VARCHAR(50) NOT NULL,
        three_year VARCHAR(50) NOT NULL,
        five_year VARCHAR(50) NOT NULL,
        seven_year VARCHAR(50) NOT NULL,
        ten_year VARCHAR(50) NOT NULL,
        twenty_year VARCHAR(50) NOT NULL,
        thirty_year VARCHAR(50) NOT NULL);
    
    CREATE TABLE constant_inflation_indexed (
        id SERIAL PRIMARY KEY UNIQUE,
        date DATE UNIQUE NOT NULL,
        long_term_average VARCHAR(50) NOT NULL);
        """
    )


connection.commit()
cursor.close()
connection.close()
