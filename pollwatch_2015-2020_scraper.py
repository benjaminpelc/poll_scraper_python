from bs4 import BeautifulSoup
from datetime import datetime as dt
import urllib

polls_url = 'http://en.wikipedia.org/wiki/Opinion_polling_for_the_next_United_Kingdom_general_election'

# get_soup
# return a BeautifulSoup opject with the full HTML from url
def get_soup(url):
    with urllib.request.urlopen(polls_url) as url:
        r = url.read()
        url.close()

    return BeautifulSoup(r, 'lxml')

# ge_poll_tables
# from a BeautifulSoup HTML object extract the tables containing general
# election poll data
def ge_poll_tables():
    return soup.find_all("table", class_="wikitable sortable collapsible")[0:2]

# Get current year
this_year = dt.now().year

soup = get_soup(polls_url)
tables = ge_poll_tables()

# print(tables[0])
# print(tables[1])
print(this_year)

# Loop through each poll results table
for tab in tables:
    rows = tab.find_all("tr")
    for row in rows:
        print(row)
        print()
    # print(tab)

