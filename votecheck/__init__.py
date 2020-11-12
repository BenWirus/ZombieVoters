from time import sleep
from fake_useragent import UserAgent
from proxyscrape import create_collector
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import requests
import random
import json
import pathlib
import math


def random_sleep(min_sec: int = 0, max_sec: int = 1):
    sec = round(random.uniform(min_sec, max_sec), 2)
    # print('Sleeping for ' + str(sec) + ' sec...')
    sleep(sec)


def is_registered(html):
    # registered = '<span class="ccd-page-heading">Yes, you are registered!</span>'
    registered = 'Yes, you are registered!'
    if registered in html:
        return True
    return False


def has_voted(html):
    if 'Ballot received' in html:
        return True
    return False


def read_json_file(file: str):
    with open(file) as json_file:
        return json.load(json_file)


def write_json_file(file: str, data):
    with open(file, 'w') as outfile:
        json.dump(data, outfile)


def get_proxy(collector: create_collector, config: dict):
    return collector.get_proxy({
        'code': config['proxy']['locations'],
        'anonymous': config['proxy']['anonymous']
    })


def format_proxies_for_requests(http, https):
    return {
        'http': 'http://' + http.host + ':' + http.port,
        'https': 'http://' + https.host + ':' + https.port,
    }


def get_user_agent():
    print('Obtaining a random user agent...')
    ua = UserAgent()
    ua.update()
    return ua.random


def save_results(results, state, county, zip_code, death_year, birth_year):
    dir_path = get_result_file_path_dir(state, county, zip_code, death_year)
    pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
    path = get_result_file_path(state, county, zip_code, death_year, birth_year)
    with open(path, 'w') as outfile:
        json.dump(results, outfile)
    print('saved results...', end=' ')


def read_results(state, county, zip_code, death_year, birth_year):
    results = []
    result_file = pathlib.Path(get_result_file_path(state, county, zip_code, death_year, birth_year))
    if result_file.is_file():
        with open(result_file, 'r') as file:
            results = json.load(file)
    return results


def get_result_file_path(state, county, zip_code, death_year, birth_year):
    dir_path = get_result_file_path_dir(state, county, zip_code, death_year)
    file = str(birth_year) + '.json'
    return dir_path + file


def get_result_file_path_dir(state, county, zip_code, death_year):
    dir_path = './output/deaths/' + state + '/' + county + '/' + str(zip_code) + '/' + str(death_year) + '/'
    return dir_path


def calculate_pagination(per_page, total):
    pages = math.ceil(float(total) / per_page)
    offset_positions = [{'page': 0, 'offset': 0}]
    for page in range(1, pages):
        offset = per_page * page
        offset_positions.append({'page': page, 'offset': offset})
    return offset_positions


def send_http_post(url, payload, headers, proxies):
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    with requests.Session() as s:
        retries = Retry(
            total=10,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            method_whitelist=frozenset(['GET', 'POST'])
        )
        s.mount('http://', HTTPAdapter(max_retries=retries))
        s.mount('https://', HTTPAdapter(max_retries=retries))
        response = s.post(
            url,
            data=payload,
            proxies=proxies,
            headers=headers,
            timeout=5.0,
            verify=False
        )
    return response
