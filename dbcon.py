"""connection to PostgreSQL db"""

# package import
import psycopg2

connection = psycopg2.connect(
    "dbname=postgres user=postgres host=database password=test port=5432"
)

cursor = connection.cursor()

cursor.execute(
    """CREATE TABLE federal_funds (
    id INT PRIMARY KEY UNIQUE NOT NULL,
    date DATE UNIQUE NOT NULL,
    rate VARCHAR(50) NOT NULL);
    """
)

cursor.execute(
    """
    CREATE TABLE scrape (           
    id INT PRIMARY KEY UNIQUE NOT NULL,
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
    "U.S. gov securities - Tresury bills - 4 week" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury bills - 3 month" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury bills - 6 month" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury bills - 1 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury - Nominal 9 - 1 month" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury - Nominal 9 - 3 month" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury - Nominal 9 - 6 month" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury - Nominal 9 - 1 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury - Nominal 9 - 2 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury - Nominal 9 - 3 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury - Nominal 9 - 5 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury - Nominal 9 - 7 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury - Nominal 9 - 10 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury - Nominal 9 - 20 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury - Nominal 9 - 30 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury - Inflation indexed - 5 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury - Inflation indexed - 7 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury - Inflation indexed - 10 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury - Inflation indexed - 20 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury - Inflation indexed - 30 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Inflation-indexed long-term average" VARCHAR(50) NOT NULL);"""
)

print(
    cursor.execute(
        """SELECT
                id,
                date,
                rate
            FROM 
                information_schema.columns
            WHERE 
                table_name = federal_funds;"""
    )
)

cursor.close()
connection.close()
