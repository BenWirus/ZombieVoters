from time import sleep
from fake_useragent import UserAgent
from proxyscrape import create_collector
import random
import json
import pathlib
import math


def random_sleep(min_sec: int = 0, max_sec: int = 1):
    sec = round(random.uniform(min_sec, max_sec), 2)
    # print('Sleeping for ' + str(sec) + ' sec...')
    sleep(sec)


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
