from votecheck import read_json_file, write_json_file, send_http_post
import json
import time
import pathlib


def send_request(proxies: dict, location: dict, birth_year: int, death_year: int, offset: int, guest_id: str,
                 bearer_token: str, useragent: str, status_only: bool = False):
    url = 'https://familygraphql.myheritage.com/search_in_historical_records/'
    payload = {
        'query': build_query_param(),
        'variables': build_variable_param(location['zip_code'], birth_year, death_year, offset),
        'guest_id': guest_id,
        'bearer_token': bearer_token,
        'description': 'search in historical records',
        'operation': ''
    }
    headers = {
        'User-Agent': useragent
    }
    response = send_http_post(url, payload, headers, proxies)
    if status_only:
        return response.status_code

    if response.status_code == 401 or response.status_code == 403:
        print('You need to obtain a new bearer_token and guest_id and place them in your config.')
        print(json.loads(response.text))
        print('Waiting for bearer token to refresh...')
        new_token = bearer_token
        while new_token == bearer_token:
            time.sleep(2)
            config = read_json_file('./config.json')
            new_token = config['myheritage']['bearer_token']
            guest_id = config['myheritage']['guest_id']
        return send_request(proxies, location, birth_year, death_year, offset, guest_id, new_token, useragent)

    if response.status_code == 429:
        print('We\'ve been sending too many requests backing off for a bit...', end=' ')
        time.sleep(60)
        print('Attempting to resume')
        return send_request(proxies, location, birth_year, death_year, offset, guest_id, bearer_token, useragent)

    return response


def build_query_param():
    return '"mutation do_search($query:EditableQuery_!){search_query_upload(id:\\"search-0\\",lang:\\"EN\\",upload_data:$query){response{summary{category_counts{... categoryFields}total{... categoryFields}}results{count data{record_type user_info{is_new is_purchased link}record{... recordFields}}}}}}fragment categoryFields on QueryResponseSummaryCategory{category_name count link}fragment recordFields on RecordBase{id name translated_name name_annotations thumbnail{url}fallback_thumbnail{url}link collection{... COLLECTION}related_photos{photo_id}hidden_fields{... FIELD}display_fields{... FIELD}}fragment COLLECTION on Collection{id name thumbnail{url}record_count short_description link is_new is_free is_temporary_free is_updated is_in_color has_images}fragment FIELD on RecordDisplayField{name label value}"'


def build_variable_param(zip_code, birth_year, death_year, offset=0):
    return json.dumps({
        'query': {
            'response_fields': [
                'summary',
                'results',
                'collection'
            ],
            'offer_free_trial': False,
            'offer_free_trial_reason': 'super search mini signup',
            'offset': offset,
            'limit': 50,
            'request': {
                'web_query': [
                    {
                        'key': 'qlivedin',
                        'value': 'Event et.livedin ep.' + str(zip_code) + ' epmo.exact'
                    },
                    {
                        'key': 'qbirth',
                        'value': 'Event et.birth ey.' + str(birth_year) + ' epmo.similar me.true mer.0'
                    },
                    {
                        'key': 'qdeath',
                        'value': 'Event et.death ey.' + str(death_year) + ' epmo.similar me.true mer.0'
                    }
                ],
                'additional_options': {
                    'fallback_policy': 'supersearch',
                    'hierarchy_context': 'collection-10002',
                    'search_form_id': 'ssdi',
                    'search_form_mode': 'advanced',
                    'use_translations': False
                }
            },
            'additional_params': []
        }
    })


def is_segment_complete(zip_code: int, death_year: int, birth_year: int):
    seg = get_segment(zip_code, death_year, birth_year)
    return seg['completed']


def get_segment_file_path(zip_code: int, death_year: int, birth_year: int):
    directory = './output/segments/'
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
    return directory + str(zip_code) + '_' + str(birth_year) + '_' + str(death_year) + '.json'


def get_segment(zip_code: int, death_year: int, birth_year: int):
    seg_file = pathlib.Path(get_segment_file_path(zip_code, death_year, birth_year))
    if seg_file.is_file():
        return read_json_file(seg_file)
    seg_data = {'completed': False, 'offset': 0}
    write_json_file(seg_file, seg_data)
    return seg_data


def put_segment(zip_code: int, death_year: int, birth_year: int, completed: bool, offset: int):
    seg_file = pathlib.Path(get_segment_file_path(zip_code, death_year, birth_year))
    write_json_file(seg_file, {'completed': completed, 'offset': offset})
    return seg_file
