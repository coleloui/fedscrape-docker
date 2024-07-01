"""Scrape fed rate"""

import requests
import csv
from bs4 import BeautifulSoup

URL = "https://www.federalreserve.gov/releases/h15/"

result = requests.get(URL, timeout=30)
doc = BeautifulSoup(result.text, "html.parser")

tr = doc.find_all("tr")

# with open('data', 'w', newline='') as file:
#     writer = csv.writer(file)

th = []

for item in tr[0]:
    if item == "\n":
        continue
    else:
        th.append(item.text)

for i, val in enumerate(tr):
    if i == 0:
        continue

    for item in val:
        row.append(item.text)

# def rowBuilder(arr):
#     for item in arr:


# print(th)
