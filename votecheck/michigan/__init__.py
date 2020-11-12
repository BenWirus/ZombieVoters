from votecheck import send_http_post
import pathlib
import json


def hunt_mi_zombie(person: dict, ua: str, proxies: dict):
    html = get_reg_status(
        person['name']['first'],
        person['name']['last'],
        person['birth']['month'],
        person['birth']['day'],
        person['location']['zip_code'],
        ua,
        proxies
    )
    save_outputs(html, person)


def save_outputs(html_results: str, person_data: dict):
    base_dir = 'output/checked/'
    file_name = '_'.join([
        person_data['location']['state'],
        person_data['location']['county'].replace(' ', ''),
        person_data['location']['zip_code'],
        person_data['name']['original'].replace(' ', '-'),
        '-'.join([
            str(person_data['birth']['month']), str(person_data['birth']['day']), str(person_data['birth']['year'])
        ]),
        '-'.join([
            str(person_data['death']['month']), str(person_data['death']['day']), str(person_data['death']['year'])
        ])
    ])

    if has_voted(html_results):
        print(' '.join([
            'voted', person_data['name']['original'], 'born', person_data['birth']['original'], 'lived',
            person_data['location']['zip_code'], 'died', person_data['death']['original']
        ]))
        base_dir = base_dir + 'zombies/balloted/'
    elif is_registered(html_results):
        print(' '.join([
            'reg', person_data['name']['original'], 'born', person_data['birth']['original'], 'lived',
            person_data['location']['zip_code'], 'died', person_data['death']['original']
        ]))
        base_dir = base_dir + 'zombies/registered/'
    else:
        print(' '.join([
            'none', person_data['name']['original'], 'born', person_data['birth']['original'], 'lived',
            person_data['location']['zip_code'], 'died', person_data['death']['original']
        ]))
        base_dir = base_dir + 'dead/'

    html_path = base_dir + 'html/'
    json_path = base_dir + 'json/'
    pathlib.Path(html_path).mkdir(parents=True, exist_ok=True)
    pathlib.Path(json_path).mkdir(parents=True, exist_ok=True)
    with open(html_path + file_name + '.html', "w") as html_file:
        html_file.write(html_results)
    with open(json_path + file_name + '.json', "w") as json_file:
        json.dump(person_data, json_file)


def is_registered(html: str):
    # registered = '<span class="ccd-page-heading">Yes, you are registered!</span>'
    registered = 'Yes, you are registered!'
    if registered in html:
        return True
    return False


def has_voted(html: str):
    if 'Ballot received' in html:
        return True
    return False


def get_reg_status(first_name: str, last_name: str, birth_month: int, birth_year: int, zip_code: str, ua: str,
                   proxies: dict):
    """
    Sends HTTP requests with form data to MI's voter registration page
    """
    # Michigan's form on https://mvic.sos.state.mi.us/Voter/Index
    url = 'https://mvic.sos.state.mi.us/Voter/SearchByName'
    # Set the user agent header to a random one
    headers = {'User-Agent': ua}
    # payload
    payload = {
        'FirstName': first_name,
        'LastName': last_name,
        'NameBirthMonth': str(birth_month),
        'NameBirthYear': str(birth_year),
        'ZipCode': zip_code,
        'Dln': None,
        'DlnBirthMonth': 0,
        'DlnBirthYear': 0,
        'DpaID': 0,
        'Months': None,
        'VoterNotFound': False,
        'TransistionVoter': False
    }
    # Send the HTTP POST with the form data
    resp = send_http_post(url, payload, headers, proxies)
    # Return the HTML
    return resp.text
