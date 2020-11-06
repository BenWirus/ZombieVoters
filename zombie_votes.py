#! /usr/bin/env python3

import pathlib
import os
import json
from time import sleep
from votecheck import michigan


def hunt_mi_zombies():
    for file in os.listdir('output/deaths/'):
        if file.endswith('.json'):
            if file.startswith('michigan_'):
                with open(os.path.join('output/deaths/', file)) as json_file:
                    persons = json.load(json_file)
                    for person in persons:
                        result_file_slug = 'michigan' + \
                                           '_' + person['last_residence']['zip'] + '_' + person['issue_year'] + \
                                           '_' + str(person['birth_date']['month']) + '_' + person['name']['first'] + \
                                           '_' + person['name']['last']
                        result_file = result_file_slug + '.html'

                        dead_file = pathlib.Path(os.path.join('output/checked/dead/', result_file))
                        zombie_file = pathlib.Path(os.path.join('output/checked/zombies/', result_file))
                        zombie_json_file = False

                        if not dead_file.is_file() and not zombie_file.is_file():
                            sleep(2)
                            response_html = michigan.get_reg_status(
                                person['name']['first'],
                                person['name']['last'],
                                person['birth_date']['month'],
                                person['birth_date']['year'],
                                person['last_residence']['zip'],
                            )

                            if response_html:
                                if michigan.is_registered(response_html):
                                    print(
                                        'Zombie found: '
                                        + person['name']['first']
                                        + ' '
                                        + person['name']['last']
                                        + ' '
                                        + str(person['birth_date']['month'])
                                        + '/'
                                        + str(person['birth_date']['year'])
                                        + ' '
                                        + person['last_residence']['zip']
                                    )
                                    output_file = zombie_file
                                    zombie_json_file = os.path.join('output/checked/zombies/',
                                                                    result_file_slug + '.json')
                                else:
                                    output_file = dead_file

                                with open(output_file, "w") as text_file:
                                    print('Saving file ' + text_file.name)
                                    text_file.write(response_html)

                                if zombie_json_file:
                                    with open(zombie_json_file, "w") as json_file_out:
                                        json.dump(person, json_file_out, indent=3, sort_keys=True)


hunt_mi_zombies()
