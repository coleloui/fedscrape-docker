-- replace with your own connection information.
-- create db
CREATE OR REPLACE DATABASE FED_DB;
-- create file format schema
CREATE OR REPLACE SCHEMA FED_DB.file_formats;
-- create csv file format
CREATE OR REPLACE file format FED_DB.file_formats.csv_fileformat
    type = csv
    field_delimiter = ','
    skip_header = 1
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

-- create different tables
CREATE OR REPLACE TABLE FED_DB.PUBLIC.federal_funds (
    date DATE,
    rate VARCHAR(50)
);
