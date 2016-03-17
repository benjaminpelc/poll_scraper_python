from bs4 import BeautifulSoup
from datetime import datetime as dt
import urllib
import re

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

# is_poll_row
# returns true if the table row contains eleven 'td' elements
def is_poll_row(row):
    return len(row.find_all("td")) == 11

# parse_poll_date
# parse the poll date from the poll row
def parse_poll_date(row):
    return { 'start_date' : "",
             'end_date' : "" }

# parse_pollster
# parse the pollster information from the poll row
def parse_pollster(row):
    return "YouGov"

# parse_client
# parse the name of the organisation that commissioned the poll
def parse_client(row):
    return "Daily Telegraph"

# strip_number_commas
# remove commas from number strings.
# e.g.
# strip_number_commas("1,234,567") = 1234567
def strip_number_commas(num_str):
    return int(num_str.replace(',', ''))

# parse_sample
# parse the sample size from the poll row html
def parse_sample(row):
    sample_size_text = row[2].get_text()
    return strip_number_commas(sample_size_text)

# parse_score_number
# get an integer from the score % string
def parse_score_number(elem):
    score_text = elem.get_text()
    if score_text == '*':
        return None
    print(score_text)
    groups = re.search(r"(^\d{1,2}\.*\d*)\%.*$", score_text)
    return float(groups.group(1))

# parse_scores
# return a dictionary containing the scores of the individual parties
def parse_scores(row):
    return { 'con' : parse_score_number(row[3]),
             'lab' : parse_score_number(row[4]),
             'ukip' : parse_score_number(row[5]),
             'ld' : parse_score_number(row[6]),
             'snp' : parse_score_number(row[7]),
             'green' : parse_score_number(row[8]),
             'other' : parse_score_number(row[9])}

# parse_poll_row
def parse_poll_row(row):
    scores = parse_scores(row)
    return { 'start_date' : parse_poll_date(row)['start_date'],
             'end_date' : parse_poll_date(row)['end_date'],
             'pollster' : parse_pollster(row),
             'client' : parse_client(row),
             'sample' : parse_sample(row),
             'con' : scores['con'],
             'lab' : scores['lab'],
             'ukip' :  scores['ukip'],
             'ld' :  scores['ld'],
             'snp' :  scores['snp'],
             'green' :  scores['green'],
             'other' :  scores['other']}

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
        if is_poll_row(row):
            row_elems = row.find_all('td')
            print(parse_poll_row(row_elems))
            print()

