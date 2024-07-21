"""This is used to pull data from the Fed."""

import requests

FED_FUND_EFFECTIVE_RATE_URL = (
    "https://www.federalreserve.gov/datadownload/Output.aspx?rel=H15&series=c5025f4bbbed155a6f17c58"
    "7772ed69e&lastobs=&from=01/01/2000&to=07/17/2024&filetype="
    "csv&label=include&layout=seriescolumn"
)

response = requests.get(FED_FUND_EFFECTIVE_RATE_URL, timeout=30)

with open("data/fed_fund_eff_rate.csv", mode="wb") as file:
    file.write(response.content)
