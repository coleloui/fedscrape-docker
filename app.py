"""base script for downloading fed rates"""

# package import
import argparse

# function import
from scrape import scrape_data
from download import bulk_download
from db_build import build_tables

# python package
parser = argparse.ArgumentParser()


def main(args):
    """Main controller application for user to decide which part of the function to run"""
    if args.all:
        scrape_data()
        bulk_download()
        return
    elif args.download:
        bulk_download()
        return
    elif args.scrape:
        scrape_data()
        return
    elif args.tables:
        build_tables()
    else:
        print("Please select one of the required flags!")


if __name__ == "__main__":

    parser.add_argument(
        "-a",
        "--all",
        dest="all",
        help="Select all actions (download and scrape)",
        action="store_true",
    )

    parser.add_argument(
        "-d",
        "--download",
        dest="download",
        help="Only Run Download",
        action="store_true",
    )
    parser.add_argument(
        "-s", "--scrape", dest="scrape", help="Only run Scrape", action="store_true"
    )

    parser.add_argument(
        "-t",
        "--tables",
        dest="tables",
        help="builds the necessary tables in the local postgres database",
        action="store_true",
    )

    args = parser.parse_args()

    main(args)
