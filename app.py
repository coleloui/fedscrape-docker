"""Scrape fed rate"""

import csv
import unicodedata
from bs4 import BeautifulSoup
import requests

# Fed URL
URL = "https://www.federalreserve.gov/releases/h15/"


def table_constructor(data):
    """Function to take html data and convert it into a
    list of lists with the intention of returning these
    to be made into a csv"""

    # Function variables
    table_data = []
    table_row = []

    # Loop through list of list to obtain and sanitize each value
    # so that if it is a number it is a float and a string is a string
    for val in data:
        for item in val:
            if item == "\n":
                continue
            else:
                # Sanitize value to get the base text
                text_string = unicodedata.normalize("NFKD", item.text).rstrip()
                # check to see if the value is a float
                try:
                    float(text_string)
                    # if so convert the value and add to list
                    table_row.append(float(text_string))
                # if not append the string
                except ValueError:
                    table_row.append(text_string)
        # append the list that is each row of the table to the overall table data
        table_data.append(table_row)
        # clear the row to a clean list for the next list
        table_row = []
    # Return list of lists that contain the sanitized values
    return table_data


# request the html from the website
result = requests.get(URL, timeout=30)
# use Beautiful Soup to parse the HTML
doc = BeautifulSoup(result.text, "html.parser")

# find all of the table rows in the parsed HTML document
html_data = doc.find_all("tr")

# call our custom function to constuct our table data
table_data_array = table_constructor(html_data)

# create a csv with the constructed data from our function
with open("data.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows(table_data_array)
