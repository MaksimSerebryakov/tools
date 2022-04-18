#!/usr/bin/env python3 

import json
import hashlib 
import os.path
import os

from datetime import datetime

EVENTS_DICT = {
    "FileCopy": ("EventType", "md5", "TargetPath", "FileName"),
    "ExecCommand" : ("EventType", "CommandText")
} 
FOLDER_NAME = '_'.join(str(datetime.now()).split('.')[0].split())

class UnknownEvent(Exception):
    def __init__(self, event):
        self.event = event
        
class EventError(Exception):
    def __init__(self, text):
        self.txt = text

"""with open('test.txt', 'r') as f:
    data = f.read()
    md5 = hashlib.md5(data.encode()).hexdigest()
    
    print(md5)    
"""

def delete_update_package():
    print('Deleting update package...')
    
def check_syntax(events):
    for event in events["Events"]:
        if not(event["EventType"] in EVENTS_DICT.keys()):
            raise UnknownEvent(event["EventType"])

        if event["EventType"] == list(EVENTS_DICT.keys())[0]:
            if len(event.keys()) != 4:
                raise EventError(
                    'Wrong keys number in events.json: expected 4, got {}'.format(
                        len(event.keys())
                    )
                )
            else:
                for arg in event.keys():
                    if not(arg in EVENTS_DICT[list(EVENTS_DICT.keys())[0]]):
                        raise EventError(
                            'Wrong list of keys in events.json'
                        )
        if event["EventType"] == list(EVENTS_DICT.keys())[1]:
            if len(event.keys()) != 2:
                raise EventError(
                    'Wrong keys number in events.json: expected 2, got {}'.format(
                        len(event.keys())
                    )
                )
            else:
                for arg in event.keys():
                    if not(arg in EVENTS_DICT[list(EVENTS_DICT.keys())[1]]):
                        raise EventError(
                            'Wrong list of keys in events.json'
                        )

def back_up(backup_path, md5, file_name, target_path, fl):
    if not(os.path.exists('{}/backup'.format(backup_path))): # check whether backup/
        os.system(                                           # exists
             'mkdir {}/backup'.format(
                backup_path
            )
        )
    
    if not(fl):                                              # update dir name = 
        os.system(                                           # current date and time
            'mkdir {0}/backup/{1}'.format(
                backup_path,
                FOLDER_NAME
            )
        )
    
    os.system(
        'sudo cp {0} {1}'.format(                            # "backing up" file
            target_path + '/' + file_name,
            backup_path + '/backup/' + FOLDER_NAME + '/' + md5
        )
    )

    with open(                                               # make file with md5:filename
        '{0}/backup/{1}/pair_table'.format(backup_path, FOLDER_NAME), 'a'
    ) as f:
        f.write('{0} {1}\n'.format(md5, target_path + '/' + file_name))

def check_md5(file_name, target_path, md5):
    pass

def exec_events(events):
    fl_backup = False
    for event in events["Events"]:
        if event["EventType"] == list(EVENTS_DICT.keys())[0]:
            if not(os.path.exists('update_package/{}'.format(
                        event["FileName"])
                    )
                ):                                                                 # check whether file 
                raise EventError(                                                  # is in update package 
                    'File {} is not in update package'.format(                     # or not
                        event["FileName"]
                    )
                )
            
            if os.path.exists('{0}/{1}'.format(
                    event["TargetPath"], 
                    event["FileName"]
                )):
                back_up(
                    events["Backup"], 
                    event["md5"], 
                    event["FileName"], 
                    event["TargetPath"], 
                    fl_backup
                )
                fl_backup = True

            os.system("cp update_package/{0} {1}/{2}".format(
                    event["FileName"], 
                    event["TargetPath"],
                    event["FileName"]
                )
            )

            check_md5()


def main():  
    events = {}
    
    with open('events.json', 'r') as events_file:
        events = json.load(events_file)
    
    check_syntax(events)
    exec_events(events)
    
    return
    
if __name__ == "__main__":
    try:
        main()
    except UnknownEvent as ue:
        print('Unknown EventType "{}" in events.json'.format(ue.event))
        delete_update_package()
    except EventError as ee:
        print(ee)
    else:
        print("update successful")
