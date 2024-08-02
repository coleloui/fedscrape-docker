-- replace with your own connection information.
-- create db
CREATE OR REPLACE DATABASE FED_DB;
-- create file format schema
CREATE OR REPLACE SCHEMA FED_DB.file_formats;
-- create csv file format
CREATE OR REPLACE file format FED_DB.file_formats.csv_fileformat
    type = csv
    field_delimiter = ','
    skip_header = 6
    null_if = ('NULL', 'null')
    empty_field_as_null = FALSE;

-- create integration obj from s3 bucket
create or replace storage integration s3_fed
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = S3
    ENABLED = TRUE
    STORAGE_AWS_ROLE_ARN = ''
    STORAGE_ALLOWED_LOCATIONS = ('')
        COMMENT = 'This is the bucket for downloading data scraped from the fed interest rates';

DESC integration s3_fed;

CREATE OR REPLACE TABLE FED_DB.PUBLIC.scrape (
    id NUMBER AUTOINCREMENT PRIMARY KEY UNIQUE NOT NULL,
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
    "U.S. gov securities - Tresury constant maturities - Nominal 9 - 1 month" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury constant maturities - Nominal 9 - 3 month" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury constant maturities - Nominal 9 - 6 month" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury constant maturities - Nominal 9 - 1 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury constant maturities - Nominal 9 - 2 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury constant maturities - Nominal 9 - 3 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury constant maturities - Nominal 9 - 5 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury constant maturities - Nominal 9 - 7 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury constant maturities - Nominal 9 - 10 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury constant maturities - Nominal 9 - 20 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury constant maturities - Nominal 9 - 30 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury constant maturities - Inflation indexed - 5 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury constant maturities - Inflation indexed - 7 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury constant maturities - Inflation indexed - 10 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury constant maturities - Inflation indexed - 20 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Tresury constant maturities - Inflation indexed - 30 year" VARCHAR(50) NOT NULL,
    "U.S. gov securities - Inflation-indexed long-term average" VARCHAR(50) NOT NULL
);

-- create different tables
CREATE OR REPLACE TABLE FED_DB.PUBLIC.federal_funds (
    id NUMBER AUTOINCREMENT PRIMARY KEY UNIQUE NOT NULL,
    date DATE UNIQUE NOT NULL,
    rate VARCHAR(50) NOT NULL
);

CREATE OR REPLACE TABLE FED_DB.PUBLIC.commercial_paper_nonfinancial (
    id NUMBER AUTOINCREMENT PRIMARY KEY UNIQUE NOT NULL,
    date DATE UNIQUE NOT NULL,
    one_month VARCHAR(50) NOT NULL,
    two_month VARCHAR(50) NOT NULL,
    three_month VARCHAR(50) NOT NULL
);
CREATE OR REPLACE TABLE FED_DB.PUBLIC.commercial_paper_financial (
    id NUMBER AUTOINCREMENT PRIMARY KEY UNIQUE NOT NULL,
    date DATE UNIQUE NOT NULL,
    one_month VARCHAR(50) NOT NULL,
    two_month VARCHAR(50) NOT NULL,
    three_month VARCHAR(50) NOT NULL
);

CREATE OR REPLACE TABLE FED_DB.PUBLIC.bank_prime_loan (
    id NUMBER AUTOINCREMENT PRIMARY KEY UNIQUE NOT NULL,
    date DATE UNIQUE NOT NULL,
    rate VARCHAR(50) NOT NULL
);

CREATE OR REPLACE TABLE FED_DB.PUBLIC.discount_window_primary_credit (
    id NUMBER AUTOINCREMENT PRIMARY KEY UNIQUE NOT NULL,
    date DATE UNIQUE NOT NULL,
    rate VARCHAR(50) NOT NULL
);

CREATE OR REPLACE TABLE FED_DB.PUBLIC.us_gov_securities_tresury_bills (
    id NUMBER AUTOINCREMENT PRIMARY KEY UNIQUE NOT NULL,
    date DATE UNIQUE NOT NULL,
    four_week VARCHAR(50) NOT NULL,
    three_month VARCHAR(50) NOT NULL,
    six_month VARCHAR(50) NOT NULL,
    one_year VARCHAR(50) NOT NULL
);

CREATE OR REPLACE TABLE FED_DB.PUBLIC.us_gov_securities_tresury_constant_maturties_nominal_9 (
    id NUMBER AUTOINCREMENT PRIMARY KEY UNIQUE NOT NULL,
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
    thirty_year VARCHAR(50) NOT NULL
);

CREATE OR REPLACE TABLE FED_DB.PUBLIC.us_gov_securities_tresury_constant_inflation_indexed (
    id NUMBER AUTOINCREMENT PRIMARY KEY UNIQUE NOT NULL,
    date DATE UNIQUE NOT NULL,
    long_term_average VARCHAR(50) NOT NULL
);