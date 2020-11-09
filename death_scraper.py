#! /usr/bin/env python3

from votecheck import read_json_file, ssdi_scraper
import sys
import getopt
import zipcodes


def run(start_year: int, end_year: int, county: str, state: str):
    print('Obtaining zip codes for ' + county + ' ' + state + '...')
    locations = zipcodes.filter_by(
        county=county.capitalize() + ' County',
        state=state.upper()
    )
    ssdi_scraper.begin(locations, start_year, end_year)
    print('Finished!')


def main(argv):
    county = ''
    state = ''
    start_year = ''
    end_year = ''
    try:
        opts, args = getopt.getopt(argv, "h:c:s:",
                                   ["start-year=", "sy=", "end-year=", "ey=", "county=", "state="])
    except getopt.GetoptError:
        print('grab_deaths.py --sy <year> --ey <year> -c <county> -s <state>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('grab_deaths.py --sy <year> --ey <year> -c <county> -s <state>')
            sys.exit()
        elif opt in ("--sy", "--start-year"):
            start_year = arg
        elif opt in ("--ey", "--end-year"):
            end_year = arg
        elif opt in ("-c", "--county"):
            county = arg
        elif opt in ("-s", "--state"):
            state = arg
    run(int(start_year), int(end_year), str(county), str(state))


if __name__ == "__main__":
    main(sys.argv[1:])
