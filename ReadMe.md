# Federal Interest Rate Downloader

This application is currently a work in progress. The intention is to keep updated records of the Federal Interest Rates so that they may be easily referenced. Eventually the plan is to be able to view this data either in specific days or over periods of time as an average.

This application is built with the intention of uploading to an S3 bucket and then loading that data into Snowflake using Snowpipe. I have attached Snowflake queries in the .sql files. You do not need to connect to either of these, but the guide is in the [Setup](#setup) section. Once the application is setup you have multiple options from the [Commands](#commands) section.

## Setup

### As a Docker Container

### To build a standalone container

```
docker build . -t fedscrape-docker:localhost
docker run -t -d fedscrape-docker:localhost
```

Then to exec into Container, get the container id and exec in

```
docker container ls
docker exec -it <CONTAINER_ID> /bin/bash
```

### As a docker compose with DB

Simply execute the compose to create DB container with python container. There is local dummy information in the docker-compose.yml that can be changed for your own postgresql if you have one set up. You will need to change the following keys.

Under python_app -> environment
```
DB_USER:
DB_PASSWORD:
DB_PORT:
```
Under database -> environment
```
POSTGRES_USER:
POSTGRES_PASSWORD:
POSTGRES_DB:
```

After run
```
docker-compose up -d --build
```

### Cloud Storage with standalone
### <ins>AWS S3</ins>

To connect to AWS and your S3 bucket, you will need to edit the docker-compose.yml to include these keys with their respective values.
Under python_app -> environment
```
AWS_KEY=
AWS_SECRET=
AWS_REGION=
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



## Commands
From here a user can execute the script as they would like

```
python app.py --tables
python app.py --all
python app.py --scrape
python app.py --download
```