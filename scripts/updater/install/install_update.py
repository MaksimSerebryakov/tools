#!/usr/bin/env python3 

import json
import hashlib 
import os.path
import os
import logging

from datetime import datetime

EVENTS_DICT = {
    "FileCopy": ("EventType", "md5", "TargetPath", "FileName"),
    "ExecCommand" : ("EventType", "CommandText")
} 
BACKUP_FOLDER_NAME = '_'.join(str(datetime.now()).split('.')[0].split())


class PackageError(Exception):
    def __init__(self, file_):
        self.type = "PackageError"
        self.file_ = file_

class UnknownEvent(Exception):
    def __init__(self, event):
        self.type = "UnknownEvent"
        self.event = event
        
class EventError(Exception):
    def __init__(self, text):
        self.type = "EventError"
        self.txt = text

class MD5Error(Exception):
    def __init__(self, file_name):
        self.type = "MD5Error"
        self.file = file_name


def make_logger():
    logger = logging.getLogger('update_logger')
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler('/var/log/update.log')
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)

    logger.addHandler(fh)

    return logger

def move_files_back():
    events = {}
    
    with open('update_package/events.json', 'r') as events_file:
        events = json.load(events_file)

    files = os.listdir(events["Backup"] + '/backup/' + BACKUP_FOLDER_NAME)
    
    for event in events["Events"]:
        if event["EventType"] == "FileCopy":
            if event["md5"] in files:
                os.system(
                    'cp {0}/backup/{1}/{2} {3}/{4}'.format(
                        events["Backup"],
                        BACKUP_FOLDER_NAME,
                        event["md5"],
                        event["TargetPath"],
                        event["FileName"]
                    )
                )

def delete_update_package(files_moved=False):
    print('\nDeleting update package...\n')
    if files_moved:
        move_files_back()

    os.system("sudo rm -rf update_package/")
    #os.system("sudo rm events.json")
    
def check_syntax(events):
    for event in events["Events"]:
        if not(event["EventType"] in EVENTS_DICT.keys()):
            raise UnknownEvent(event["EventType"])

        if event["EventType"] == list(EVENTS_DICT.keys())[0]:
            if len(event.keys()) != 4:
                raise EventError(
                    'Wrong "Events" keys number in events.json for "FileCopy"\
: expected 4, got {}'.format(
                        len(event.keys())
                    )
                )
            else:
                for arg in event.keys():
                    if not(arg in EVENTS_DICT[list(EVENTS_DICT.keys())[0]]):
                        raise EventError(
                            'Wrong list of "Events" keys in events.json for\
FileCopy'
                        )
        if event["EventType"] == list(EVENTS_DICT.keys())[1]:
            if len(event.keys()) != 2:
                raise EventError(
                    'Wrong "Events" keys number in events.json: for ExecCommand\
expected 2, got {}'.format(
                        len(event.keys())
                    )
                )
            else:
                for arg in event.keys():
                    if not(arg in EVENTS_DICT[list(EVENTS_DICT.keys())[1]]):
                        raise EventError(
                            'Wrong list of keys in events.json for ExecCommand'
                        )

def back_up(backup_path, md5, file_name, target_path, fl):
    if not(os.path.exists('{}/backup'.format(backup_path))): # check whether backup/
        os.system(                                           # exists
             'mkdir {}/backup'.format(
                backup_path
            )
        )
    
    if not(fl):                                              # backup dir name = 
        os.system(                                           # current date and time
            'mkdir {0}/backup/{1}'.format(
                backup_path,
                BACKUP_FOLDER_NAME
            )
        )
    
    os.system(
        'sudo cp {0} {1}'.format(                            # "backing up" file
            target_path + '/' + file_name,
            backup_path + '/backup/' + BACKUP_FOLDER_NAME + '/' + md5
        )
    )

    if not(os.path.exists('{0}/backup/{1}/pair_table.json'.format(
        backup_path, 
        BACKUP_FOLDER_NAME))
    ):  
        os.system('echo {0}{1} > {2}/backup/{3}/pair_table.json'.format(
            '{',
            '}',
            backup_path, 
            BACKUP_FOLDER_NAME
        ))

    pairs = {}
    with open(                                               # make file with md5:filename
        '{0}/backup/{1}/pair_table.json'.format(backup_path, BACKUP_FOLDER_NAME), 'r'
    ) as f:
        pairs = json.load(f)

    pairs[md5] = file_name

    with open(                                               # make file with md5:filename
        '{0}/backup/{1}/pair_table.json'.format(backup_path, BACKUP_FOLDER_NAME), 'w'
    ) as f:
        json.dump(pairs, f)

def check_md5(file_name, target_path, md5):
    with open('{0}/{1}'.format(
        target_path,
        file_name
    ), 'r') as f:
        data = f.read()
        md5_new = hashlib.md5(data.encode()).hexdigest()
    
        if md5 != md5_new:
            raise MD5Error('{}/{}'.format(
                target_path, 
                file_name
            ))

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

            check_md5(
                event["FileName"],
                event["TargetPath"],
                event["md5"]
            )
        if event["EventType"] == list(EVENTS_DICT.keys())[1]:
            if not(os.system(event["CommandText"])):
                continue

def add_err_to_config(error_type):
    config = {}
    with open('config_path', 'r') as cfg_path:
        path = cfg_path.read()
        with open(path, 'r') as config_file:
            config = json.load(config_file)

    if not("Errors" in config.keys()):
        config["Errors"] = {}

    config["Errors"] = {
        error_type.type : {
            "Date": ' '.join(BACKUP_FOLDER_NAME.split('_')), 
            "read" : False
        }
    }

    with open('config_path', 'r') as cfg_path:
        path = cfg_path.read()
        with open(path, 'w') as config_file:
            json.dump(config, config_file, indent=4)

def add_new_files_to_config():
    config = {}
    with open('config_path', 'r') as cfg_path:
        path = cfg_path.read()
        with open(path, 'r') as config_file:
            config = json.load(config_file)
    config["New"] = list()

    events = {}
    with open('update_package/events.json', 'r') as events_file:
        events = json.load(events_file)

    for event in events["Events"]:
        if event["EventType"] == "FileCopy":
            config["New"].append(
                {
                    "hash" : event["md5"],
                    "path" : event["TargetPath"] + '/' + event["FileName"]
                }
            )
    
    with open('config_path', 'r') as cfg_path:
        path = cfg_path.read()
        with open(path, 'w') as config_file:
            json.dump(config, config_file, indent=4)

def main(): 
    if not(os.path.exists('update_package')):
        print("update_package/ is missing...")
        raise PackageError('update_package/')
    if not(os.path.exists('update_package/events.json')):
        print("events.json is missing...")
        raise PackageError('events.json')
    
    events = {}
    
    with open('update_package/events.json', 'r') as events_file:
        events = json.load(events_file)
    
    check_syntax(events)
    exec_events(events)

if __name__ == "__main__":
    try:
        main()
    except UnknownEvent as ue:
        logger = make_logger()
        logger.error(
            'Unknown EventType "{}" in events.json'.format(
                ue.event
            )
        )

        add_err_to_config(ue)

        print('Unknown EventType "{}" in events.json'.format(ue.event))
        delete_update_package()
    except EventError as ee:
        logger = make_logger()
        logger.error(ee)

        add_err_to_config(ee)

        print(ee)

        delete_update_package()
    except MD5Error as md5er:
        logger = make_logger()
        logger.error(
            'File "{}" was coppied incorrectly, md5-s do not match'.format(
                md5er.file
            )
        )

        add_err_to_config(md5er)

        print(md5er.file)

        delete_update_package(files_moved=True)
    except PackageError as pe:
        logger = make_logger()
        logger.error(
            'File {} is missing, unable to start update'.format(
                pe.file_
            )
        )

        add_err_to_config(pe)
    else:
        logger = make_logger()
        logger.info('Updated successfully')

        add_new_files_to_config()

        print("Updated successfully!")
        delete_update_package()
