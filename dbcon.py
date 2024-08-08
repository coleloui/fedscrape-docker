"""connection to PostgreSQL db"""

# package import
import psycopg2

connection = psycopg2.connect(
    "dbname=postgres user=postgres host=database password=test port=5432"
)

cursor = connection.cursor()

# cursor.execute(
#     """CREATE TABLE federal_funds (
#     id SERIAL PRIMARY KEY UNIQUE,
#     date DATE UNIQUE NOT NULL,
#     rate VARCHAR(50) NOT NULL);
#     """
# )

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

connection.commit()
cursor.close()
connection.close()
