"""Scrape fed rate"""

import csv
import unicodedata
import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np

# Fed URL
URL = "https://www.federalreserve.gov/releases/h15/"
# URL = "https://en.wikipedia.org/wiki/History_of_Python"


def table_constructor(data):
    """Function to take html data and convert it into a
    list of lists with the intention of returning these
    to be made into a csv"""

    # Function variables
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
    holding = []
    # indecies to skip for no informtaion
    # we use this because it is possible for no data to exist
    # in a column but these rows specificially do not ever contain data
    skip = [2, 3, 7, 13, 14, 19, 20, 32]

    for i, value in enumerate(data):
        if i in skip:
            continue
        else:
            for j, item in enumerate(value):
                text_string = unicodedata.normalize("NFKD", item.text).strip()
                if int((j - 1) / 2) == 0 or j % 2 == 0:
                    continue
                else:
                    try:
                        float(text_string)
                        holding.append(float(text_string))
                    except ValueError:
                        holding.append(text_string)
            if len(holding) == 0:
                continue
            else:
                linked.append(holding)
                holding = []

    data_dict = dict(zip(table_column, linked))
    df = pd.DataFrame(data=data_dict, index=None)
    return df


# request the html from the website
result = requests.get(URL, timeout=30)
# use Beautiful Soup to parse the HTML
doc = BeautifulSoup(result.text, "html.parser")
# find all of the table rows in the parsed HTML document
html_data = doc.find(id="h15table")
table_data = html_data.findChildren("tr")

# call our custom function to constuct our table data
table_df = table_constructor(table_data)
# retreive exsiting data
csv_df = pd.DataFrame.read_csv("./data.csv")
print(csv_df)

# create a csv with the constructed data from our function
# with open("data.csv", "a+", newline="", encoding="utf-8") as file:
#     writer = csv.writer(file)
#     writer.writerows(table_data_array)
