# Written by: Katerina Bosko
import json
import csv
from collections import defaultdict

def main():
    with open('companies_final.json', 'r') as f:
        companies_json = json.load(f)


    # calculate missing data
    no_desc = 0
    no_headq = 0

    for company in companies_json:
        if company['desc'] == "-1":
            no_desc += 1
        if company['headquarters'] == "-1":
            no_headq += 1

    print("BEFORE CLEANING:")
    print(f"missing headquarters - {no_headq}, missing description - {no_desc}")


    # DATA CLEANING
    # 1. getting states and encoding companies w/o state as international
    # 2. clean descriptions (some of them end abruptly in the middle of the sentence)

    us_state_abbrev = {
        'Alabama': 'AL',
        'Alaska': 'AK',
        'American Samoa': 'AS',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'District of Columbia': 'DC',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Guam': 'GU',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Northern Mariana Islands':'MP',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Puerto Rico': 'PR',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virgin Islands': 'VI',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY'
    }

    for company in companies_json:
        splitted = company['headquarters'].split(',')
        try:
            if splitted[1].strip() in us_state_abbrev.keys():
                company['state'] = splitted[1].strip()
        except:
            if splitted[0] == '-1':
                company['state'] = '-1'
            else:
                company['state'] = 'International'

        # split description so that it ends with "."
        if company['desc'] != "-1":
            splitted = company['desc'].split(".")
            company['desc'] = ".".join(splitted[:-1])+"."


    # DEALING WITH MISSING DATA
    # 1. add missing information about the state for universities
    # in our list from topcolleges.csv file
    # 2. add missing information for universities in our list if the name has a state in its name
    # 3. substitute manually for the remaining companies w/o state
    colleges_dict = defaultdict(list)
    with open('topcolleges.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            colleges_dict[row['Name']].append(row['State'])

    # reversed dictionary of states
    abbrev_us_state = dict(map(reversed, us_state_abbrev.items()))


    # manual substitution for the remaining companies w/o state
    states_for_missing_dict = {'SUNY, Buffalo (University at Buffalo)': 'New York',
    'AstraZeneca': 'International',
    'GlaxoSmithKline': 'International',
    'CWT': 'Minnesota',
    'BP': 'International',
    'Washington University in Saint Louis': 'Missouri'}


    for company in companies_json:
        # double substitution - find state abbrv from topcolleges
        # and add full state name based on abbrev_us_state dictionary
        if company['name'] in colleges_dict.keys():
            state_abbrv = colleges_dict[company['name']][0]
            if state_abbrv in abbrev_us_state:
                company['state'] = abbrev_us_state[state_abbrv]

        # if universities have state in their names
        if company['state'] == '-1':
                for state in us_state_abbrev:
                    if state in company['name']:
                        company['state'] = state

        # substitute manually from states_for_missing_dict
        if company['state'] == '-1':
            company['state'] = states_for_missing_dict[company['name']]

        # there is 1 company with missing data for employees adding manually data
        if company['name'] == 'Consolidated Electrical Distributors':
            company['employees'] = 6000

        # there is 1 company with wrong location attribution
        if company['name'] == 'University of Illinois-Urbana-Champaign':
            company['state'] = 'Illinois'



    # calculate missing states after cleaning
    no_state = 0
    for company in companies_json:
        if company['state'] == "-1":
            no_state += 1
    print("AFTER CLEANING:")
    print(f"missing states - {no_state}")

    with open('companies_clean.json', 'w') as f:
        json.dump(companies_json, f, indent=3)


if __name__ == "__main__":
    main()
