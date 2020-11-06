#! /usr/bin/env python3

from selenium import webdriver
from nameparser import HumanName
from time import sleep
import dateparser
import sys
import getopt
import json


def read_config():
    with open('config.json') as json_file:
        config = json.load(json_file)
        return config


def save_results(results, county, state, year, page):
    path = 'output/deaths/' + state + '_' + county + '_' + str(year) + '_' + str(page) + '.json'
    with open(path, 'w') as outfile:
        json.dump(results, outfile, indent=3, sort_keys=True)
    print('Saved results: ' + path)


def login(chrome: webdriver.Chrome, username: str, password: str):
    chrome.get('https://www.ancestry.com/account/signin')

    login_form_iframe = chrome.find_element_by_id("signInFrame")
    chrome.switch_to.frame(login_form_iframe)

    username_input = chrome.find_element_by_id("username")
    password_input = chrome.find_element_by_id("password")
    login_button = chrome.find_element_by_id("signInBtn")

    username_input.send_keys(username)
    password_input.send_keys(password)
    login_button.click()


def parse_row(row: str, record: dict):
    entry = row.split(':')
    if entry[0].strip() == 'Name':
        entry.pop(0)
        n = HumanName(':'.join(entry).strip())
        name = n.as_dict()
        name['original'] = n.original
        record['name'] = name
    if entry[0].strip() == 'Social Security Number':
        entry.pop(0)
        record['ssn'] = ':'.join(entry)
    if entry[0].strip() == 'Birth Date':
        entry.pop(0)
        d = dateparser.parse(':'.join(entry).strip())
        date = {
            'day': d.day,
            'month': d.month,
            'year': d.year,
            'original': ':'.join(entry).strip()
        }
        record['birth_date'] = date
    if entry[0].strip() == 'Issue Year':
        entry.pop(0)
        record['issue_year'] = ':'.join(entry).strip()
    if entry[0].strip() == 'Issue State':
        entry.pop(0)
        record['issue_state'] = ':'.join(entry).strip()
    if entry[0].strip() == 'Last Residence':
        entry.pop(0)
        original = ':'.join(entry).strip()
        parts = original.split(', ')

        try:
            int(parts[0])
            zip = str(parts[0])
        except Exception:
            zip = False

        addr = {
            'zip': zip,
            'original': original
        }

        record['last_residence'] = addr
    if entry[0].strip() == 'Death Date':
        entry.pop(0)
        d = dateparser.parse(':'.join(entry).strip())
        date = {
            'day': d.day,
            'month': d.month,
            'year': d.year,
            'original': ':'.join(entry).strip()
        }
        record['death_date'] = date

    return record


def scrape(chrome: webdriver.Chrome, page: int, year: int, county: str, state: str, page_cooldown_sec: int):
    url = 'https://www.ancestry.com/search/collections/3693/?pg=' + str(page) + '&residence=' + \
          str(year) + '_' + county + '-' + state + '-usa&residence_x=_1-0'
    chrome.get(url)
    sleep(2)
    hrefs = chrome.find_elements_by_xpath("//a[@href]")
    links = []
    records = []

    for href in hrefs:
        if href.text and href.text == 'View Record':
            links.append(href.get_attribute("href"))

    for link in links:
        record = {'link': link}
        chrome.get(link)
        sleep(page_cooldown_sec)
        for row in chrome.find_elements_by_xpath("//tr"):
            record = parse_row(str(row.text), record)

        if record['last_residence']['zip']:
            records.append(record)

    return records


def run(year: int, page: int, county: str, state: str):
    config = read_config()
    max_year = int(config['max_year'])
    max_page = int(config['max_page'])
    print(
        'Scraping death records from ' + str(year) + ' - ' + str(max_year) + ' for ' + county + ' county ' + state +
        '. ' + 'Starting at page ' + str(page) + ' ending at page ' + str(max_page) + '.'
    )
    chrome = webdriver.Chrome('./chromedriver')
    chrome.maximize_window()
    login(chrome, config['username'], config['password'])
    sleep(2)

    # Main loop
    while year <= max_year:
        while page <= max_page:
            page_results = scrape(chrome, page, year, county, state, config['page_cooldown_sec'])
            save_results(page_results, county, state, year, page)
            page += 1
        year += 1

    chrome.close()
    exit()


def main(argv):
    year = ''
    page = ''
    county = ''
    state = ''
    try:
        opts, args = getopt.getopt(argv, "hy:p:c:s:", ["year=", "page=", "county=", "state="])
    except getopt.GetoptError:
        print('grab_deaths.py -y <year> -p <page> -c <county> -s <state>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('grab_deaths.py -y <year> -p <page> -c <county> -s <state>')
            sys.exit()
        elif opt in ("-y", "--year"):
            year = arg
        elif opt in ("-p", "--page"):
            page = arg
        elif opt in ("-c", "--county"):
            county = arg
        elif opt in ("-s", "--state"):
            state = arg
    run(int(year), int(page), str(county), str(state))


if __name__ == "__main__":
    main(sys.argv[1:])
