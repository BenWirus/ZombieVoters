from nameparser import HumanName
from votecheck import random_sleep, get_proxy, get_user_agent, format_proxies_for_requests, calculate_pagination, \
    save_results, read_results, read_json_file
from votecheck.ssdi_scraper.utils import send_request, get_segment, put_segment
from votecheck import michigan
from proxyscrape import create_collector
import dateparser
import json


def begin(locations: list, start_year: int = 1900, end_year: int = 2014):
    config = read_json_file('./config.json')
    proxies = {}
    guest_id = config['myheritage']['guest_id']
    bearer_token = config['myheritage']['bearer_token']
    user_agent = get_user_agent()
    per_page = 50

    if config['proxy']['enable']:
        print('Obtaining http & https proxies...')
        http_collector = create_collector('http-collector', 'http')
        https_collector = create_collector('https-collector', 'https')
        proxies = format_proxies_for_requests(get_proxy(http_collector, config), get_proxy(https_collector, config))

    for death_year in range(start_year, end_year + 1):
        for birth_year in range(start_year, death_year + 1):
            for location in locations:
                config = read_json_file('./config.json')
                segment = get_segment(location['zip_code'], death_year, birth_year)
                if not segment['completed']:  # This segment is not completed yet
                    print('Querying for deaths in the year ' + str(death_year) + ' that were born in ' +
                          str(birth_year) + ' that lived in ' + str(location['zip_code'] + '...'), end=" ")
                    offset = 0
                    result = send_request(
                        proxies,
                        location,
                        birth_year,
                        death_year,
                        offset,
                        guest_id,
                        bearer_token,
                        user_agent
                    )
                    data = json.loads(result.text)
                    total = data['data']['search_query_upload']['response']['results']['count']
                    print('Found ' + str(total) + ' results.')

                    if total > 0:  # At least one page of data
                        print('processing page 0...', end=' ')
                        records = data['data']['search_query_upload']['response']['results']['data']
                        process_results(records, location, death_year, birth_year, user_agent)

                        if total > per_page:  # Handle multiple pages of data
                            pages = calculate_pagination(per_page, total)
                            for page in pages:
                                if page > 0:
                                    offset = page['offset']
                                    result = send_request(
                                        proxies,
                                        location,
                                        birth_year,
                                        death_year,
                                        page['offset'],
                                        guest_id,
                                        bearer_token,
                                        user_agent
                                    )
                                    print('processing page ' + str(page['page']) + '...', end=' ')
                                    data = json.loads(result.text)
                                    records = data['data']['search_query_upload']['response']['results']['data']
                                    process_results(records, location, death_year, birth_year, user_agent)
                                    random_sleep(config['cool_down']['min'], config['cool_down']['max'])

                        print(' done!')

                    put_segment(location['zip_code'], death_year, birth_year, True, offset)
                    random_sleep(config['cool_down']['min'], config['cool_down']['max'])
                else:
                    print(
                        'Skipping completed segment ' +
                        str(location['zip_code']) +
                        '-' + str(death_year) +
                        '-' + str(birth_year)
                    )


def process_results(items: list, location: dict, death_year: int, birth_year: int, ua):
    results = read_results(location['state'], location['county'], location['zip_code'], death_year, birth_year)
    for item in items:
        name = item['record']['name']
        n = HumanName(name)
        name = n.as_dict()
        name['original'] = n.original
        birth = {}
        death = {}
        for field in item['record']['display_fields']:
            if field['name'] == 'birth':
                b = dateparser.parse(field['value'])
                birth = {
                    'day': b.day,
                    'month': b.month,
                    'year': b.year,
                    'original': field['value']
                }
            if field['name'] == 'death':
                d = dateparser.parse(field['value'])
                death = {
                    'day': d.day,
                    'month': d.month,
                    'year': d.year,
                    'original': field['value']
                }
        person = {
            'name': name,
            'location': location,
            'birth': birth,
            'death': death
        }
        results.append(person)

        if location['state'] == 'MI':
            michigan.hunt_mi_zombie(person, ua)

    save_results(results, location['state'], location['county'], location['zip_code'], death_year, birth_year)
