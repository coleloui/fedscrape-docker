"""base script for downloading fed rates"""

# package import
import sys

# function import
from scrape import scrape_data
from request_data import bulk_download

# python package
# update this script to use click instead of argv


def main(call):
    """Main controller application for user to decide which part of the function to run"""
    match call:
        case "A":
            scrape_data()
            bulk_download()
            return
        case "a":
            scrape_data()
            bulk_download()
            return
        case "D":
            bulk_download()
            return
        case "d":
            bulk_download()
            return
        case "S":
            scrape_data()
            return
        case "s":
            scrape_data()
            return
        case _:
            print("Please select one of the required flags!")


command = sys.argv[1]

if __name__ == "__main__":
    main(command)
