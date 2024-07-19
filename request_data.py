"""This is used to pull data from the Fed."""

import requests

FFER_URL = (
    "https://www.federalreserve.gov/datadownload/Download.aspx?rel=H15&series=c5025f4bbbed155"
    "a6f17c587772ed69e&filetype=csv&label=include&layout=seriescolumn&from=01/01/2000&to=07/17/2024"
)

response = requests.get(FFER_URL, timeout=30)

with open("data/ffer.csv", mode="wb") as file:
    file.write(response.content)
