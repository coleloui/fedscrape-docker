"""Scrape fed rate"""

import csv
import unicodedata
import pandas as pd
from bs4 import BeautifulSoup
import requests

# Fed URL
URL = "https://www.federalreserve.gov/releases/h15/"
# URL = "https://en.wikipedia.org/wiki/History_of_Python"


def table_constructor(data):
    """Function to take html data and convert it into a
    list of lists with the intention of returning these
    to be made into a csv"""

    # Function variables
    table_dict = {
        "Date": [],
        "Federal funds": [],
        "Commercial Paper - Nonfinancial - 1 Month": [],
        "Commercial Paper - Nonfinancial - 2 Month": [],
        "Commercial Paper - Nonfinancial - 3 Month": [],
        "Commercial Paper - Financial - 1 Month": [],
        "Commercial Paper - Financial - 2 Month": [],
        "Commercial Paper - Financial - 3 Month": [],
        "Bank prime loan": [],
        "Discount window primary credit": [],
        "U.S. gov securities - Tresury bills - 4 week": [],
        "U.S. gov securities - Tresury bills - 3 month": [],
        "U.S. gov securities - Tresury bills - 6 month": [],
        "U.S. gov securities - Tresury bills - 1 year": [],
        "U.S. gov securities - Tresury constant maturities - Nominal 9 - 1 month": [],
        "U.S. gov securities - Tresury constant maturities - Nominal 9 - 3 month": [],
        "U.S. gov securities - Tresury constant maturities - Nominal 9 - 6 month": [],
        "U.S. gov securities - Tresury constant maturities - Nominal 9 - 1 year": [],
        "U.S. gov securities - Tresury constant maturities - Nominal 9 - 2 year": [],
        "U.S. gov securities - Tresury constant maturities - Nominal 9 - 3 year": [],
        "U.S. gov securities - Tresury constant maturities - Nominal 9 - 5 year": [],
        "U.S. gov securities - Tresury constant maturities - Nominal 9 - 7 year": [],
        "U.S. gov securities - Tresury constant maturities - Nominal 9 - 10 year": [],
        "U.S. gov securities - Tresury constant maturities - Nominal 9 - 20 year": [],
        "U.S. gov securities - Tresury constant maturities - Nominal 9 - 30 year": [],
        "U.S. gov securities - Tresury constant maturities - Inflation indexed - 5 year": [],
        "U.S. gov securities - Tresury constant maturities - Inflation indexed - 7 year": [],
        "U.S. gov securities - Tresury constant maturities - Inflation indexed - 10 year": [],
        "U.S. gov securities - Tresury constant maturities - Inflation indexed - 20 year": [],
        "U.S. gov securities - Tresury constant maturities - Inflation indexed - 30 year": [],
        "U.S. gov securities - Inflation-indexed long-term average": [],
    }

    # use keys in table_dict to place data
    linked = []
    holding = []
    for value in data:
        for j, item in enumerate(value):
            text_string = unicodedata.normalize("NFKD", item.text).rstrip()
            if int((j - 1) / 2) == 0 or j % 2 == 0 or text_string == "":
                continue
            else:
                holding.append(text_string.strip())
        if len(holding) == 0:
            continue
        else:
            linked.append(holding)
            holding = []
    print(len(linked))
    #         try:
    #             float(text_string)
    #             # if so convert the value and add to list
    #             table_dict[int((j - 1) / 2)].append(float(text_string))
    #         # if not append the string
    #         except ValueError:
    #             table_dict[int((j - 1) / 2)].append(text_string)

    # Loop through list of list to obtain and sanitize each value
    # so that if it is a number it is a float and a string is a string
    # for i, item in enumerate(data):

    # text_string = unicodedata.normalize("NFKD", item.text).rstrip()

    # if text_string == "\n":
    #     continue
    # else:
    #     # Sanitize value to get the base text
    #     # check to see if the value is a float
    #     try:
    #         float(text_string)
    #         # if so convert the value and add to list
    #         table_dict[i].append(float(text_string))
    #     # if not append the string
    #     except ValueError:
    #         table_dict[i].append(text_string)
    # append the list that is each row of the table to the overall table data

    # Return list of lists that contain the sanitized values
    return table_dict


# request the html from the website
result = requests.get(URL, timeout=30)
# use Beautiful Soup to parse the HTML
doc = BeautifulSoup(result.text, "html.parser")
# find all of the table rows in the parsed HTML document
html_data = doc.find(id="h15table")
table_data = html_data.findChildren("tr")


# dfs = pd.read_html(URL})
# print(len(dfs))

# call our custom function to constuct our table data
table_data_dict = table_constructor(table_data)
# print(table_data_dict)


# create a csv with the constructed data from our function
# with open("data.csv", "a+", newline="", encoding="utf-8") as file:
#     writer = csv.writer(file)
#     writer.writerows(table_data_array)
