"""script for scraping data from fed interest rate table and formatting"""

# package import
import unicodedata
import pandas as pd
from bs4 import BeautifulSoup
import requests

# function import
from upload import upload_scrape, test_connection


def table_constructor(data):
    """Function to take html data and convert it into a list of lists
    with the intention of returning these to be made into a csv"""

    # Function variables
    # this is the title of the columns we will be using in snowflake to match our data
    table_column = [
        "Date",
        "Federal funds",
        "Commercial Paper - Nonfinancial - 1 Month",
        "Commercial Paper - Nonfinancial - 2 Month",
        "Commercial Paper - Nonfinancial - 3 Month",
        "Commercial Paper - Financial - 1 Month",
        "Commercial Paper - Financial - 2 Month",
        "Commercial Paper - Financial - 3 Month",
        "Bank prime loan",
        "Discount window primary credit",
        "U.S. gov securities - Tresury bills - 4 week",
        "U.S. gov securities - Tresury bills - 3 month",
        "U.S. gov securities - Tresury bills - 6 month",
        "U.S. gov securities - Tresury bills - 1 year",
        "U.S. gov securities - Tresury constant maturities - Nominal 9 - 1 month",
        "U.S. gov securities - Tresury constant maturities - Nominal 9 - 3 month",
        "U.S. gov securities - Tresury constant maturities - Nominal 9 - 6 month",
        "U.S. gov securities - Tresury constant maturities - Nominal 9 - 1 year",
        "U.S. gov securities - Tresury constant maturities - Nominal 9 - 2 year",
        "U.S. gov securities - Tresury constant maturities - Nominal 9 - 3 year",
        "U.S. gov securities - Tresury constant maturities - Nominal 9 - 5 year",
        "U.S. gov securities - Tresury constant maturities - Nominal 9 - 7 year",
        "U.S. gov securities - Tresury constant maturities - Nominal 9 - 10 year",
        "U.S. gov securities - Tresury constant maturities - Nominal 9 - 20 year",
        "U.S. gov securities - Tresury constant maturities - Nominal 9 - 30 year",
        "U.S. gov securities - Tresury constant maturities - Inflation indexed - 5 year",
        "U.S. gov securities - Tresury constant maturities - Inflation indexed - 7 year",
        "U.S. gov securities - Tresury constant maturities - Inflation indexed - 10 year",
        "U.S. gov securities - Tresury constant maturities - Inflation indexed - 20 year",
        "U.S. gov securities - Tresury constant maturities - Inflation indexed - 30 year",
        "U.S. gov securities - Inflation-indexed long-term average",
    ]
    # use keys to place data
    linked = []
    row_data = []

    # indecies to skip for no informtaion we use this because it is possible for
    # no data to existin a column but these rows specificially do not ever contain data
    skip = [2, 3, 7, 13, 14, 19, 20, 32]

    for i, value in enumerate(data):
        # if the current index is in a row that we dont need data from we skip it
        if i in skip:
            continue
        else:
            for j, item in enumerate(value):
                # sanitize all data to get the raw string
                text_string = unicodedata.normalize("NFKD", item.text).strip()
                # these removes any data that isnt there or is a new line
                if int((j - 1) / 2) == 0 or j % 2 == 0:
                    continue
                else:
                    # add the string to the row_data list
                    row_data.append(text_string)
            # if the row_data list is empty move to the next
            if len(row_data) == 0:
                continue
            # if the row_data list has values add them to the linked list
            # set the row_data to an empty list for the next row
            else:
                linked.append(row_data)
                row_data = []

    # create a dictionary by zipping the table_column list to the linked list
    data_dict = dict(zip(table_column, linked))
    # create a Data Frame from the previously created dictionary
    df = pd.DataFrame(data=data_dict, index=None)
    return df


def scrape_data():
    """Function to fetch web scraped data from federal reserve"""

    # Fed URL
    url = "https://www.federalreserve.gov/releases/h15/"

    # request the html from the website
    result = requests.get(url, timeout=30)

    # use Beautiful Soup to parse the HTML
    doc = BeautifulSoup(result.text, "html.parser")

    # find all of the table rows in the parsed HTML document
    html_data = doc.find(id="h15table")
    table_data = html_data.findChildren("tr")

    # call our custom function to constuct a DataFrame
    table_df = table_constructor(table_data)
    # conver DataFrame to CSV
    table_df.to_csv("scrape/scrape.csv", index=False)
    print("scraped data in directory scrape")

    if test_connection():
        upload_scrape()
