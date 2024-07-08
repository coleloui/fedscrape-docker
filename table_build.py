"""File for table_constructor fundtion"""

import unicodedata
import pandas as pd


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
