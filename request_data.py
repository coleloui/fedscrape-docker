"""This is used to pull data from the Fed."""

from concurrent.futures import ThreadPoolExecutor
import requests

BASE_URL = (
    "https://www.federalreserve.gov/datadownload/Output.aspx?rel=H15&series={series}"
    "&lastobs=&from=01/01/2000&to={current}&filetype=csv&label=include&layout=seriescolumn"
)

URLS = {
    # Federal funds effective rate
    "fed_eff": BASE_URL.format(
        series="c5025f4bbbed155a6f17c587772ed69e", current="07/17/2024"
    ),
    # Federal funds Nonfinancial Commercial Paper Interest rate
    "non_com": BASE_URL.format(
        series="ca2dd1ccd5102a49176c86b6646496c3", current="07/17/2024"
    ),
}


# response = requests.get(FED_FUND_EFFECTIVE_RATE_URL, timeout=30)

# with open("data/fed_fund_eff_rate.csv", mode="wb") as file:
#     file.write(response.content)
