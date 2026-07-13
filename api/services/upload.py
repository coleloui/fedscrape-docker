"""Optional S3 upload service — port of upload.py."""

import os

from api.config import settings


def _s3_resource():
    import boto3
    return boto3.Session(
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_KEY,
        aws_secret_access_key=settings.AWS_SECRET,
    ).resource("s3")


def s3_available() -> bool:
    """Return True only when all S3 credentials are set."""
    return all([settings.AWS_KEY, settings.AWS_SECRET, settings.AWS_REGION, settings.S3_BUCKET])


def upload_scrape_csv(path: str = "scrape/scrape.csv") -> None:
    """Upload the scrape CSV to S3."""
    s3 = _s3_resource()
    with open(path, "rb") as fh:
        s3.Object(settings.S3_BUCKET, "data/scrape/scrape.csv").put(Body=fh)
    print("S3 upload complete: scrape.csv")


def upload_download_dir(src_dir: str = "download") -> None:
    """Upload all downloaded CSVs in src_dir to S3."""
    s3 = _s3_resource()
    for root, _dirs, files in os.walk(src_dir):
        for fname in files:
            if fname == ".gitkeep":
                continue
            series_name = os.path.basename(root)
            full_path = os.path.join(root, fname)
            with open(full_path, "rb") as fh:
                s3.Object(settings.S3_BUCKET, f"data/{series_name}/{fname}").put(Body=fh)
            print(f"S3 upload complete: {series_name}/{fname}")
