#!/usr/bin/env python3
 
import json
import hashlib
import os
import os.path
import sys

def add_file_to_package(file_path):
    os.system('cp {0} {1}/'.format(
        file_path, 
        'update_package'
    ))

def build_update():
    events = {}
    
    print('\nNow enter the sequence of files and commands\
\nwhich should be coppied or executed one by another:\n')
    events["Events"] = list()
    
    file_ = ''
    command = ''
    type = ''

    while type != 'exit':
        print('Command type: ', end='')
        type = input()
        
        event = {}

        if type == 'file':
            print('Enter full path to file: ', end='')
            file_ = input()
            if not(os.path.exists(file_)):
                print('No such file or directory')
                continue

            add_file_to_package(file_)

            print('Enter target path: ', end='')
            target_path = input()

            md5 = ''
            with open(file_, 'r') as f:
                data = f.read()
                md5 = hashlib.md5(data.encode()).hexdigest()
            
            event = {
                "EventType": "FileCopy",
                "md5": md5,
                "TargetPath": target_path,
                "FileName": file_.split('/')[-1]
            }
        elif type == 'command':
            print('Enter command: ', end='')
            command = input()

            event = {
                "EventType": "ExecCommand",
                "CommandText": command
            }
        elif type != 'exit':
            print('Unknown command type')
        else:
            break
        
        events["Events"].append(event)
    
    return events

def main():
    events = {}
    os.system('mkdir update_package')

    if len(sys.argv) == 1:
        events = build_update()
    else:
        with open(sys.argv[1], 'r') as event_file:
            events = json.load(event_file)

    print('Choose Backup folder: ', end='')
    backup = input()
    events["Backup"] = backup
    
    with open('update_package/events.json', 'w') as event_file:
        json.dump(events, event_file, indent=4)

if __name__ == "__main__":
    main()