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
cursor = connection.cursor()


def build_tables():
    """Builds the tables in the postgres database"""

    cursor.execute(
        """
    CREATE TABLE scrape (
        id SERIAL PRIMARY KEY UNIQUE NOT NULL,
        date DATE UNIQUE NOT NULL,
        "Federal Funds" VARCHAR(50),
        "Commercial Paper - Nonfinancial - 1 Month" VARCHAR(50),
        "Commercial Paper - Nonfinancial - 2 Month" VARCHAR(50),
        "Commercial Paper - Nonfinancial - 3 Month" VARCHAR(50),
        "Commercial Paper - Financial - 1 Month" VARCHAR(50),
        "Commercial Paper - Financial - 2 Month" VARCHAR(50),
        "Commercial Paper - Financial - 3 Month" VARCHAR(50),
        "Bank Prime Loan" VARCHAR(50),
        "Discount Window Primary Credit" VARCHAR(50),
        "U.S. Gov - Bills - 4 week" VARCHAR(50),
        "U.S. Gov - Bills - 3 month" VARCHAR(50),
        "U.S. Gov - Bills - 6 month" VARCHAR(50),
        "U.S. Gov - Bills - 1 year" VARCHAR(50),
        "U.S. Gov - Maturities - Nominal 9 - 1 month" VARCHAR(50),
        "U.S. Gov - Maturities - Nominal 9 - 3 month" VARCHAR(50),
        "U.S. Gov - Maturities - Nominal 9 - 6 month" VARCHAR(50),
        "U.S. Gov - Maturities - Nominal 9 - 1 year" VARCHAR(50),
        "U.S. Gov - Maturities - Nominal 9 - 2 year" VARCHAR(50),
        "U.S. Gov - Maturities - Nominal 9 - 3 year" VARCHAR(50),
        "U.S. Gov - Maturities - Nominal 9 - 5 year" VARCHAR(50),
        "U.S. Gov - Maturities - Nominal 9 - 7 year" VARCHAR(50),
        "U.S. Gov - Maturities - Nominal 9 - 10 year" VARCHAR(50),
        "U.S. Gov - Maturities - Nominal 9 - 20 year" VARCHAR(50),
        "U.S. Gov - Maturities - Nominal 9 - 30 year" VARCHAR(50),
        "U.S. Gov - Maturities - Inflation indexed - 5 year" VARCHAR(50),
        "U.S. Gov - Maturities - Inflation indexed - 7 year" VARCHAR(50),
        "U.S. Gov - Maturities - Inflation indexed - 10 year" VARCHAR(50),
        "U.S. Gov - Maturities - Inflation indexed - 20 year" VARCHAR(50),
        "U.S. Gov - Maturities - Inflation indexed - 30 year" VARCHAR(50),
        "U.S. Gov - Inflation-Indexed Long-Term Average" VARCHAR(50)
        );
        
    CREATE TABLE federal_eff_funds (
        id SERIAL PRIMARY KEY UNIQUE,
        date DATE UNIQUE NOT NULL,
        rate VARCHAR(50)
        );

    CREATE TABLE commercial_paper_nonfinancial (
        id SERIAL PRIMARY KEY UNIQUE,
        date DATE UNIQUE NOT NULL,
        one_month VARCHAR(50),
        two_month VARCHAR(50),
        three_month VARCHAR(50)
        );

    CREATE TABLE commercial_paper_financial (
        id SERIAL PRIMARY KEY UNIQUE,
        date DATE UNIQUE NOT NULL,
        one_month VARCHAR(50),
        two_month VARCHAR(50),
        three_month VARCHAR(50)
        );
    
    CREATE TABLE bank_prime_loan (
        id SERIAL PRIMARY KEY UNIQUE,
        date DATE UNIQUE NOT NULL,
        rate VARCHAR(50)
        );
 
    CREATE TABLE discount_window_primary_credit (
        id SERIAL PRIMARY KEY UNIQUE,
        date DATE UNIQUE NOT NULL,
        rate VARCHAR(50)
        );
    
    CREATE TABLE us_gov_securities_tresury_bills (
        id SERIAL PRIMARY KEY UNIQUE,
        date DATE UNIQUE NOT NULL,
        four_week VARCHAR(50),
        three_month VARCHAR(50),
        six_month VARCHAR(50),
        one_year VARCHAR(50)
        );
    
    CREATE TABLE maturities_nominal_9 (
        id SERIAL PRIMARY KEY UNIQUE,
        date DATE UNIQUE NOT NULL,
        one_month VARCHAR(50),
        three_month VARCHAR(50),
        six_month VARCHAR(50),
        one_year VARCHAR(50),
        two_year VARCHAR(50),
        three_year VARCHAR(50),
        five_year VARCHAR(50),
        seven_year VARCHAR(50),
        ten_year VARCHAR(50),
        twenty_year VARCHAR(50),
        thirty_year VARCHAR(50)
        );
    
    CREATE TABLE maturities_inflation_indexed (
        id SERIAL PRIMARY KEY UNIQUE,
        date DATE UNIQUE NOT NULL,
        five_year VARCHAR(50),
        seven_year VARCHAR(50),
        ten_year VARCHAR(50),
        twenty_year VARCHAR(50),
        thirty_year VARCHAR(50)
        );
    
    CREATE TABLE inflation_indexed_long_term (
        id SERIAL PRIMARY KEY UNIQUE,
        date DATE UNIQUE NOT NULL,
        long_term_average VARCHAR(50)
        );
        """
    )

    connection.commit()
    cursor.close()
    connection.close()
