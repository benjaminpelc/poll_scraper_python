from bs4 import BeautifulSoup
import datetime as dt
import urllib
import re
import pandas as pd

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

# month_string_to_number
def month_string_to_number(month_str):
    months = { 'Jan' : 1, 'Feb' : 2, 'Mar' : 3, 'Apr' : 4,
               'May' : 5, 'Jun' : 6, 'Jul' : 7, 'Aug' : 8,
               'Sep' : 9, 'Oct' : 10, 'Nov' : 11, 'Dec' : 12 }
    return months[month_str]

def date_format_1(row, year):
    date_string = row[0].get_text()
    regex = r"(\d{1,2}).(\d{1,2})\s(\w{3})"
    search_results = re.search(regex, date_string)
    if (search_results):
        start_day_str = search_results.group(1)
        end_day_str = search_results.group(2)
        month_str = search_results.group(3)

        month = month_string_to_number(month_str)

        start_date = dt.date(year, month, int(start_day_str))
        end_date = dt.date(year, month, int(end_day_str))

        dates = { 'start_date' : start_date, 'end_date' : end_date }
        return dates
    else:
        return None

def date_format_3(row, year):
    date_string = row[0].get_text()
    regex = r"(\d{1,2})\s(\w{3})"
    search_results = re.search(regex, date_string)
    if (search_results):
        start_day_str = search_results.group(1)
        month_str = search_results.group(2)
        month = month_string_to_number(month_str)

        start_date = dt.date(year, month, int(start_day_str))

        dates = { 'start_date' : start_date, 'end_date' : start_date }
        return dates
    else:
        return None

# parse_poll_date
# parse the poll date from the poll row
def parse_poll_date(row, year):
    # date_format_1(row, year)

    # if
    return date_format_1(row, year) or date_format_3(row, year) or { 'start_date' : "", 'end_date' : "" }

# parse_pollster_client_string
# get the pollster and the client from the polllster/client string
def parse_pollster_client_string(row):
    pollster_client_string = row[1].get_text()
    groups = re.search(r"^(\w+)\/{0,1}(.*)", pollster_client_string)
    return { 'pollster' : groups.group(1),
             'client' : groups.group(2) }

# parse_pollster
# parse the pollster information from the poll row
def parse_pollster(row):
    return parse_pollster_client_string(row)['pollster']

# parse_client
# parse the name of the organisation that commissioned the poll
def parse_client(row):
    return parse_pollster_client_string(row)['client']

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
#
# Clean this up
def parse_score_number(elem):
    score_text = elem.get_text()
    if score_text == '*':
        return None
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
def parse_poll_row(row, year):
    scores = parse_scores(row)
    return { 'start_date' : parse_poll_date(row, year)['start_date'],
             'end_date' : parse_poll_date(row, year)['end_date'],
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
this_year = dt.datetime.now().year
soup = get_soup(polls_url)
tables = ge_poll_tables()

# print(tables[0])
# print(tables[1])
print(this_year)

# Loop through each poll results table
table_counter = 0
polls = []
for tab in tables:
    year = this_year - table_counter
    rows = tab.find_all("tr")
    for row in rows:
        if is_poll_row(row):
            row_elems = row.find_all('td')
            poll = (parse_poll_row(row_elems, year))
            polls.append(poll)
    table_counter += 1

print(polls)

polls_df = pd.DataFrame.from_records(polls, index='start_date')
polls_df = polls_df[['end_date' , 'pollster', 'client', 'sample',
                     'con', 'lab', 'ukip', 'ld', 'snp', 'green', 'other' ]]
polls_df.to_csv('polls.csv')
print(polls_df.head())

