from Key import key
from requests import get
from datetime import timedelta
from dateutil import parser
import time
import json


'''
This Project Queries all the List from NY Times API and saves them as JSON Files,
Which later can be added to the db or analyzed directly from Python

Example Query
https://api.nytimes.com/svc/books/v3/lists/current/hardcover-fiction.json?api-key=yourkey
'''

main_query = 'https://api.nytimes.com/svc/books/v3/lists/'

# Gets List of all possible NY Times list
data = get(f'{main_query}names.json?api-key={key}')

all_list = list()

# Saves Results of Lists
for item in data.json()['results']:
   all_list.append (item)

# AS each list has start and end date and the list is regularly updated inbetween
# we will need function that can itterate through dates
def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

# main script
for item in all_list:

    # gets Start Date, End Date and the name of the List
    start_date = parser.parse(item['oldest_published_date']).date()
    end_date = parser.parse(item['newest_published_date']).date()
    list_name = item['list_name']

    # Initializes list where gathered ratings will be saved
    all_items_within_list = list()

    # To check how many times we itterate though list
    step = 0

    for single_date in daterange(start_date, end_date):

        data = get(f'{main_query}/{single_date}/{list_name}.json?api-key={key}')

        # Some lists are weekly others bi weekly and others daily,
        # As it is not clear we will query though all dates.
        # If for this specific date result is returned and the result is not already in the list
        # we save it in the main list

        if data.status_code == 200 and data.json() not in all_items_within_list:
            all_items_within_list.append(data.json())

            # Step is only printed if the request was succesful. It makes easier to see what is frequency of
            # List updates
            print(step)

        # to check where we at
        step += 1
        # to make sure that not too many request are sent simulteniously
        time.sleep(5)

    #Save Json file with the same name as the name of the list
    with open(f'{list_name}.json', 'w', encoding='utf-8') as outfile:
        json.dump(all_items_within_list, outfile, ensure_ascii=False, indent=2)


