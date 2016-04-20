#! /usr/bin/env python

from bs4 import BeautifulSoup
import datetime as dt
import urllib
import re
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib import style
style.use('ggplot')

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
    return {
               'Jan' : 1, 'Feb' : 2, 'Mar' : 3, 'Apr' : 4,
               'May' : 5, 'Jun' : 6, 'Jul' : 7, 'Aug' : 8,
               'Sep' : 9, 'Oct' : 10, 'Nov' : 11, 'Dec' : 12
           }[month_str]

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

        start_date = start_date.isoformat()
        end_date = end_date.isoformat()

        return {
                    'start_date' : start_date,
                    'end_date' : start_date
               }
    else:
        return None

def date_format_2(row, year):
    date_string = row[0].get_text()
    regex = r"(\d{1,2})\s(\w{3})\w*.*(\d{1,2})\s(\w{3})"
    search_results = re.search(regex, date_string)
    if (search_results):
        start_day_str = search_results.group(1)
        end_day_str = search_results.group(3)
        start_month_str = search_results.group(2)
        end_month_str = search_results.group(4)

        start_month = month_string_to_number(start_month_str)
        end_month = month_string_to_number(end_month_str)

        start_date = dt.date(year, start_month, int(start_day_str))
        end_date = dt.date(year, end_month, int(end_day_str))

        start_date = start_date.isoformat()
        end_date = end_date.isoformat()

        return {
                    'start_date' : start_date,
                    'end_date' : start_date
               }
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
        start_date = start_date.isoformat()

        return {
                    'start_date' : start_date,
                    'end_date' : start_date
               }
    else:
        return None

# parse_poll_date
# parse the poll date from the poll row
def parse_poll_date(row, year):
    return (
                date_format_1(row, year) or
                date_format_2(row, year) or
                date_format_3(row, year) or
                { 'start_date' : "", 'end_date' : "" }
            )

# parse_pollster_client_string
# get the pollster and the client from the pollster/client string
def parse_pollster_client_string(row):
    pollster_client_string = row[1].get_text()
    search_regex = r"^([a-zA-Z ]+)\/{0,1}(.*)"
    groups = re.search(search_regex, pollster_client_string)
    return {
               'pollster' : groups.group(1),
               'client' : groups.group(2).replace(", ", "/")
           }

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

# round_float_string_to_int
def round_float_string_to_int(float_str):
    return int(round(float(float_str)))

# parse_score_number
# get an integer from the score % string
def parse_score_number(elem):
    score_text = elem.get_text()
    search_regex = r"(^\d{1,2}\.*\d*)\%.*$"

    # check for edge cases where a score may not be present.
    if score_text == '*' or score_text == '-':
        return None

    groups = re.search(search_regex, score_text)
    return round_float_string_to_int(groups.group(1))

# parse_scores
# return a dictionary containing the scores of the individual parties
def parse_scores(row):
    return {
                'con' : parse_score_number(row[3]),
                'lab' : parse_score_number(row[4]),
                'ukip' : parse_score_number(row[5]),
                'ldem' : parse_score_number(row[6]),
                'snp' : parse_score_number(row[7]),
                'grn' : parse_score_number(row[8]),
                'other' : parse_score_number(row[9])
            }

# parse_poll_row
def parse_poll_row(row, year):
    scores = parse_scores(row)
    return {
                'startDate' : parse_poll_date(row, year)['start_date'],
                'endDate' : parse_poll_date(row, year)['end_date'],
                'pollster' : parse_pollster(row),
                'client' : parse_client(row),
                'sample' : parse_sample(row),
                'con' : scores['con'],
                'lab' : scores['lab'],
                'ukip' :  scores['ukip'],
                'ldem' :  scores['ldem'],
                'snp' :  scores['snp'],
                'grn' :  scores['grn'],
                'other' :  scores['other']
             }

# poll_list_to_dataframe
# return a pandas dataframe from a list of poll dictionaries.
def poll_list_to_dataframe(raw_list):
    return pd.DataFrame.from_records(polls, index='startDate')[[
                    'endDate' , 'pollster', 'client', 'sample',
                     'con', 'lab', 'ukip', 'ldem', 'snp', 'grn',
                     'other'
                     ]]

# Do some scraping and put in  a Pandas dataframe.
# Get current year
soup = get_soup(polls_url)
tables = ge_poll_tables()

# Loop through each poll results table
table_counter = 0
polls = []
this_year = dt.datetime.now().year
for tab in tables:
    year = this_year - table_counter
    rows = tab.find_all("tr")
    for row in rows:
        if is_poll_row(row):
            row_elems = row.find_all('td')
            poll = parse_poll_row(row_elems, year)
            polls.append(poll)
    # increment the table counter so year can be adjusted
    table_counter += 1

polls_df = poll_list_to_dataframe(polls)

polls_df.to_csv('polls.csv')
polls_df.to_json('polls.json', orient='records')
print(polls_df.head(15))

# just_scores = polls_df[[ 'con', 'lab', 'ukip', 'ldem', 'snp', 'grn', 'other' ]]
# just_scores.plot()
# plt.show()
