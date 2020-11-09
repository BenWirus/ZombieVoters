import requests
from requests.packages.urllib3.util.retry import Retry
from votecheck import random_sleep, get_user_agent


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


def get_reg_status(first_name: str, last_name: str, birth_month: int, birth_year: int, zip_code: str):
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

    url = 'https://mvic.sos.state.mi.us/Voter/SearchByName'

    headers = {
        'User-Agent': get_user_agent()
    }

    tries = 0
    max_tries = 3

    while tries <= max_tries:
        try:
            tries += 1
            resp = requests.post(url, data={
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
            }, headers=headers, verify=False, timeout=2.000)
            return resp.text
        except Exception:
            if tries <= max_tries:
                random_sleep(1, 3)
            else:
                return False
