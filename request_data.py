"""Script to download csv files of fed interest rate data."""

# package import
from concurrent.futures import ThreadPoolExecutor
import requests

# function import
from upload import upload_download

# Base URL that gets formatted for the respective and rate and date
BASE_URL = (
    "https://www.federalreserve.gov/datadownload/Output.aspx?rel=H15&series={series}"
    "&lastobs=&from=01/01/2000&to={current_date}&filetype=csv&label=include&layout=seriescolumn"
)

# URLS to iterate through when retreiving data. This is a dictionary because it allows
# us to define the title of the directory as well as formatting the URL in one
URLS = {
    # Federal funds effective rate
    "fed_eff": BASE_URL.format(
        series="c5025f4bbbed155a6f17c587772ed69e", current_date="07/17/2024"
    ),
    # Federal funds Nonfinancial Commercial Paper Interest rate
    "comm_non_fin": BASE_URL.format(
        series="ca2dd1ccd5102a49176c86b6646496c3", current_date="07/17/2024"
    ),
    "comm_fin": BASE_URL.format(
        series="268dcdcf1b746c42fb990fe2107b7dad", current_date="07/17/2024"
    ),
    "bank_prime": BASE_URL.format(
        series="02338be6957591cdba0a59c6f09b8389", current_date="07/17/2024"
    ),
    "discount_window": BASE_URL.format(
        series="e048853c9a3f0734b8538f508828f298", current_date="07/17/2024"
    ),
    "tresury_bills": BASE_URL.format(
        series="4ab494d223ec49ec01fe09b49c6d17da", current_date="07/17/2024"
    ),
    "nominal_9": BASE_URL.format(
        series="bf17364827e38702b42a58cf8eaa3f78", current_date="07/17/2024"
    ),
    "inflation_indexed": BASE_URL.format(
        series="a5efc8cebeae2f178010054da08cb1f1", current_date="07/17/2024"
    ),
    "inflation_long_term": BASE_URL.format(
        series="68447ee78d1e78718e4a96db9405d605", current_date="07/17/2024"
    ),
}


def download_file(data):
    """Function to download files from url"""
    # unpacking the tuple
    title, url = data
    # Try to request the csv from the Federal database
    try:
        response = requests.get(url, timeout=30)

        with open(f"./download/{title}/{title}.csv", mode="wb") as file:
            file.write(response.content)
        print(f"Downloaded file {title}")

        response.raise_for_status()

    # Catch possible errors and return from the function to go to the next link or finish the map
    except requests.exceptions.HTTPError as err:
        print(f"{title} did not download due to {err}")
        return
    except requests.exceptions.Timeout:
        print(f"{title} was not downloaded due to timeout")
        return
    except requests.exceptions.TooManyRedirects:
        print(f"{title} was not downloaded, check that the URL is correct")
        return
    except requests.exceptions.RequestException as e:
        print(f"{title} was not downloaded")
        print(e)
        return


def bulk_download():
    """Function to iterate through URL dict and pass tuple to the download file function"""
    with ThreadPoolExecutor() as executor:
        executor.map(download_file, URLS.items())

    # upload_download()


bulk_download()
