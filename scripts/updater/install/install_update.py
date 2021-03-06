#!/usr/bin/env python3 

import json
import hashlib 
import os.path
import os
import logging
import sys 

from datetime import datetime

BACKUP = 'backup'
EVENTS = 'Events'
EVENT_TYPE = 'EventType'
FILE_COPY = 'FileCopy'
MD5 = 'md5'
EXEC_COMMAND = 'ExecCommand'
FILE_REMOVE = 'FileRemove'
CONFIG_PATH_JSON = 'config_path.json'
FILE_NAME = 'FileName'
TARGET_PATH = 'TargetPath'
COMMAND_TEXT = 'CommandText'
ERRORS = 'Errors'
CONFIG = 'config'
NEW = 'New'
REMOVE = 'Remove'
EVENTS_DICT = {
    FILE_COPY: (EVENT_TYPE, MD5, TARGET_PATH, FILE_NAME),
    EXEC_COMMAND : (EVENT_TYPE, COMMAND_TEXT),
    FILE_REMOVE: (EVENT_TYPE, TARGET_PATH)
} 
BACKUP_FOLDER_NAME = '_'.join(str(datetime.now()).split('.')[0].split())

class PackageError(Exception):
    def __init__(self, file_):
        self.type = 'PackageError'
        self.file_ = file_

class UnknownEvent(Exception):
    def __init__(self, event):
        self.type = 'UnknownEvent'
        self.event = event
        
class EventError(Exception):
    def __init__(self, text):
        self.type = 'EventError'
        self.txt = text

class MD5Error(Exception):
    def __init__(self, file_name):
        self.type = 'MD5Error'
        self.file = file_name

class PathError(Exception):
    def __init__(self, path):
        self.type = 'PathError'
        self.path = path


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
    
    config_path = ''
    for i in range(len(sys.argv[0].split('/')) - 1):
        config_path += sys.argv[0].split('/')[i] + '/'
    config_path += CONFIG_PATH_JSON
    
    backup = ''
    with open(config_path, 'r') as cfg_path:
        backup = json.load(cfg_path)[BACKUP]
    
    if not(os.path.exists(backup + '/backup/' + BACKUP_FOLDER_NAME)):
        return

    files = os.listdir(backup + '/backup/' + BACKUP_FOLDER_NAME)
    
    for event in events[EVENTS]:
        if event[EVENT_TYPE] == FILE_COPY:
            if event[MD5] in files:
                os.system(
                    'cp {0}/backup/{1}/{2} {3}/{4}'.format(
                        backup,
                        BACKUP_FOLDER_NAME,
                        event[MD5],
                        event[TARGET_PATH],
                        event[FILE_NAME]
                    )
                )

def delete_update_package(files_moved=False):
    print('\nDeleting update package...\n')
    if files_moved:
        move_files_back()

    os.system('sudo rm -rf update_package/')
    #os.system('sudo rm events.json')
    
def check_syntax(events):
    for event in events[EVENTS]:
        if not(event[EVENT_TYPE] in EVENTS_DICT.keys()):
            raise UnknownEvent(event[EVENT_TYPE])

        if event[EVENT_TYPE] == FILE_COPY:
            if len(event.keys()) != 4:
                raise EventError(
                    'Wrong "Events" keys number in events.json for "FileCopy"\
: expected 4, got {}'.format(
                        len(event.keys())
                    )
                )
            else:
                for arg in event.keys():
                    if not(arg in EVENTS_DICT[FILE_COPY]):
                        raise EventError(
                            'Wrong list of "Events" keys in events.json for\
FileCopy'
                        )
        if event[EVENT_TYPE] == EXEC_COMMAND:
            if len(event.keys()) != 2:
                raise EventError(
                    'Wrong "Events" keys number in events.json: for ExecCommand\
\nexpected 2, got {}'.format(
                        len(event.keys())
                    )
                )
            else:
                for arg in event.keys():
                    if not(arg in EVENTS_DICT[EXEC_COMMAND]):
                        raise EventError(
                            'Wrong list of keys in events.json for ExecCommand'
                        )
        if event[EVENT_TYPE] == FILE_REMOVE:
            if len(event.keys()) != 2:
                raise EventError(
                    'Wrong "Events" keys number in events.json: for FileRemove\
\nexpected 2, got {}'.format(
                        len(event.keys())
                    )
                )
            else:
                for arg in event.keys():
                    if not(arg in EVENTS_DICT[FILE_REMOVE]):
                        raise EventError(
                            'Wrong list of keys in events.json for FileRemove'
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
    ), 'rb') as f:
        data = f.read()
        md5_new = hashlib.md5(data).hexdigest()
    
        if md5 != md5_new:
            raise MD5Error('{}/{}'.format(
                target_path, 
                file_name
            ))

def exec_events(events):
    config_path = ''
    for i in range(len(sys.argv[0].split('/')) - 1):
        config_path += sys.argv[0].split('/')[i] + '/'
    config_path += CONFIG_PATH_JSON
    
    backup = ''
    with open(config_path, 'r') as cfg_path:
        backup = json.load(cfg_path)[BACKUP]
        
    fl_backup = False
    
    for event in events[EVENTS]:
        type_ = event[EVENT_TYPE]
        if type_ == FILE_COPY:
            if not(os.path.exists('update_package/{}'.format(
                        event[MD5])
                    )
                ):                                                                 # check whether file 
                raise EventError(                                                  # is in update package 
                    'File {} is not in update package'.format(                     # or not
                        event[FILE_NAME]
                    )
                )
            
            if os.path.exists('{0}/{1}'.format(
                    event[TARGET_PATH], 
                    event[FILE_NAME]
                )):
                back_up(
                    backup, 
                    event[MD5], 
                    event[FILE_NAME], 
                    event[TARGET_PATH], 
                    fl_backup
                )
                fl_backup = True
            else:
                if not(os.path.exists('{0}/'.format(
                    event[TARGET_PATH]
                ))):
                    raise PathError('{0}/{1}'.format(
                        event[TARGET_PATH], 
                        event[FILE_NAME]
                    ))

            os.system('cp update_package/{0} {1}/{2}'.format(
                    event[MD5], 
                    event[TARGET_PATH],
                    event[FILE_NAME]
                )
            )

            check_md5(
                event[FILE_NAME],
                event[TARGET_PATH],
                event[MD5]
            )
        if type_ == FILE_REMOVE:
            if not(os.path.exists(event[TARGET_PATH])):
                raise PathError(event[TARGET_PATH])
            
            md5 = ''
            with open(event[TARGET_PATH], 'rb') as f:
                data = f.read()
                md5 = hashlib.md5(data).hexdigest()
            
            back_up(
                backup,
                md5,
                event[TARGET_PATH].split('/')[-1],
                '/'.join(event[TARGET_PATH].split('/')[:-1]),
                fl_backup
            )

            os.system('sudo rm {}'.format(
                event[TARGET_PATH]
            ))

        if type_ == EXEC_COMMAND:
            if not(os.system(event[COMMAND_TEXT])):
                continue

def add_err_to_config(error_type):
    config = {}
    
    config_path = ''
    for i in range(len(sys.argv[0].split('/')) - 1):
        config_path += sys.argv[0].split('/')[i] + '/'
    config_path += CONFIG_PATH_JSON
    
    with open(config_path, 'r') as cfg_path:
        path = json.load(cfg_path)[CONFIG]
        with open(path, 'r') as config_file:
            config = json.load(config_file)
    
    if not(ERRORS in config.keys()):
        config[ERRORS] = {}

    config[ERRORS] = {
        error_type.type : {
            'Date': ' '.join(BACKUP_FOLDER_NAME.split('_')), 
            'read' : False
        }
    }

    with open(config_path, 'r') as cfg_path:
        path = json.load(cfg_path)[CONFIG]
        with open(path, 'w') as config_file:
            json.dump(config, config_file, indent=4)

def add_new_files_to_config():
    config = {}
    
    config_path = ''
    for i in range(len(sys.argv[0].split('/')) - 1):
        config_path += sys.argv[0].split('/')[i] + '/'
    config_path += CONFIG_PATH_JSON
    
    with open(config_path, 'r') as cfg_path:
        path = json.load(cfg_path)[CONFIG]
        with open(path, 'r') as config_file:
            config = json.load(config_file)
    config[NEW] = {}
    config[REMOVE] = {}

    events = {}
    with open('update_package/events.json', 'r') as events_file:
        events = json.load(events_file)

    cntr_new = 0
    cntr_remove = 0
    for event in events[EVENTS]:
        if event[EVENT_TYPE] == FILE_COPY:
            config[NEW][str(cntr_new)] = {
                    'hash' : event[MD5],
                    'path' : event[TARGET_PATH] + '/' + event[FILE_NAME]
                }
            cntr_new += 1
        if event[EVENT_TYPE] == FILE_REMOVE:
            config[REMOVE][str(cntr_remove)] = {
                    'path' : event[TARGET_PATH]
                }
            cntr_remove += 1
    
    with open(config_path, 'r') as cfg_path:
        path = json.load(cfg_path)[CONFIG]
        with open(path, 'w') as config_file:
            json.dump(config, config_file, indent=4)

def main(): 
    if not(os.path.exists('update_package')):
        print('update_package/ is missing...')
        raise PackageError('update_package/')
    if not(os.path.exists('update_package/events.json')):
        print('events.json is missing...')
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

        print('eeeeeeeeee', ee)

        delete_update_package()
    except MD5Error as md5er:
        logger = make_logger()
        logger.error(
            'File "{}" was coppied incorrectly, md5-s do not match'.format(
                md5er.file
            )
        )

        add_err_to_config(md5er)

        print(MD5, md5er.file)

        delete_update_package(files_moved=True)
    except PackageError as pe:
        logger = make_logger()
        logger.error(
            'File {} is missing, unable to start update'.format(
                pe.file_
            )
        )

        add_err_to_config(pe)
    except PathError as pathe:
        logger = make_logger()
        logger.error(
            '{} no such file or directory'.format(
                pathe.path
            )
        )
            
        print(
            '{} no such file or directory'.format(
                pathe.path
            )
        )
        
        add_err_to_config(pathe)
        delete_update_package(files_moved=True)
    else:
        logger = make_logger()
        logger.info('Updated successfully')

        add_new_files_to_config()

        print('Updated successfully!')
        delete_update_package()
