import requests
from time import sleep
from requests.packages.urllib3.util.retry import Retry


def is_registered(html):
    # registered = '<span class="ccd-page-heading">Yes, you are registered!</span>'
    registered = 'Yes, you are registered!'
    if registered in html:
        return True
    return False


def get_reg_status(first_name: str, last_name: str, birth_month: int, birth_year: int, zip_code: str):
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    url = 'https://mvic.sos.state.mi.us/Voter/SearchByName'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36 OPR/72.0.3815.186'
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
                sleep(2)
            else:
                return False
