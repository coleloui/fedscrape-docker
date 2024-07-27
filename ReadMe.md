# Federal Interest Rate Downloader

This application is currently a work in progress. The intention is to keep updated records of the Federal Interest Rates so that they may be easily referenced. Eventually the plan is to be able to view this data either in specific days or over periods of time as an average.

This application is built with the intention of uploading to an S3 bucket and then loading that data into Snowflake using Snowpipe. I have attached Snowflake queries in the .sql files. You do not need to connect to either of these, but the guide is in the [Setup](#setup) section.

To get started right away please view the [Quickstart](#Quickstart) section below

## Quickstart

### <ins>Enter the following commands in your terminal to set up the application from the root of the application</ins>

Create and enter virtual environment

```
$ virtualenv -p python3 .venv && source .venv/bin/activate
```

Install packages

```
$ pip3 install -r requirements.txt
```

Create necessary files

```
$ touch .env && printf "AWS_KEY=\nAWS_SECRET=\nS3_BUCKET=" >> .env
```

### <ins>After the application has been set up choose which command to run</ins>

Run both the Web Scrape and

## Setup

### <ins>AWS S3</ins>

To connect to AWS and your S3 bucket, you will need to go into the .env that you created from the quickstart and fill out your credentials.

```
AWS_KEY=
AWS_SECRET=
S3_BUCKET=
```

### <ins>Snowflake</ins>

For Snowflake to tie into your S3 bucket you will need to create a Role in IAM for your bucket permissions and get your role arn.

Query to set up your integration where you put in your arn and allowed locations.

```
create or replace storage integration <title>
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = S3
    ENABLED = TRUE
    STORAGE_AWS_ROLE_ARN = ''
    STORAGE_ALLOWED_LOCATIONS = ('')
        COMMENT = 'This is the bucket for downloading data scraped from the fed interest rates';
```

Query to describe your integration to obtain the STORAGE_AWS_EXTERNAL_ID from the result and your edit the trust relationship in your role in IAM to be the ExternalID.

```
DESC integration <title>;
```
