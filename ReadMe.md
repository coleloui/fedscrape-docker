# Federal Interest Rate Downloader

This application is currently a work in progress. You must currently run either request_data.py or scrape.py individually.

This application is built with the intention of uploading to an S3 bucket, personally I have attached Snowflake and Snowpipe to this for auto loading. You dont need to do this but all of the Snowflake SQL queries will be in the .sql files.

**YOU DO NOT NEED TO CONNECT TO A S3 BUCKET OR SNOWFLAKE FOR THIS APPLICATION TO RUN**

## Setup

### AWS S3

To get this running you just need to run the script and you'll have that individual or group of csv's downloaded. For full functionality you need to create a .env file. Inside of this .env you will need the following

```
AWS_KEY=
AWS_SECRET=
S3_BUCKET=
```

your k.key in upload.py should be the directory in your s3 bucket where you want your file to end up.

### Snowflake

For Snowflake to tie into your S3 bucket you will need to create a role in IAM for your bucket permissions and get your role arn and then in
Snowflake you need to set up your integration where you put in your arn and allowed locations. Run this SQL query and then describe your integration to obtain the STORAGE_AWS_EXTERNAL_ID from the result and your edit the trust relationship in your role in IAM to be the ExternalID.

```
create or replace storage integration <title>
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = S3
    ENABLED = TRUE
    STORAGE_AWS_ROLE_ARN = ''
    STORAGE_ALLOWED_LOCATIONS = ('')
        COMMENT = 'This is the bucket for downloading data scraped from the fed interest rates';
```

```
DESC integration <title>;
```
