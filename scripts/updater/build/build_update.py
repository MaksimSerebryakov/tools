#!/usr/bin/env python3
 
import json
import hashlib
import os
import os.path
import sys

from datetime import datetime

UPDATE_FOLDER_NAME = str(datetime.now()).split('.')[0].split()[0]

def add_file_to_package(file_path, md5):
    os.system('cp {0} {1}/{2}'.format(
        file_path, 
        'update_package',
        md5
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

            print('Enter target path: ', end='')
            target_path = input()

            md5 = ''
            with open(file_, 'rb') as f:
                data = f.read()
                md5 = hashlib.md5(data).hexdigest()
                
            add_file_to_package(file_, md5)
            
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
        elif type == 'remove':
            print('Enter remote path of file you want to remove: ', end='')
            remove_path = input()
            
            event = {
                "EventType": "FileRemove",
                "TargetPath": remove_path
            }
        elif type != 'exit':
            print('Unknown command type')
            continue
        else:
            break
        
        events["Events"].append(event)
    
    return events

def handle_update(info_file):
    info = {}
    events = {}
    events["Events"] = list()
    
    with open(info_file, 'r') as f:
        info = json.load(f)
        
    for event in info["Events"]:
        if event["EventType"] == 'FileCopy':
            add_file_to_package(
                event["LocalPath"],
                event["md5"]
            )
            events["Events"].append({
                    "md5": event["md5"],
                    "FileName": event["FileName"],
                    "EventType": event["EventType"],
                    "TargetPath": event["TargetPath"]
            })
        else:
            events["Events"].append(event)
        
        
    return events

def rewrite_updates(info_file):
    info = {}
    updates = {}
    updates['updates'] = {}
    
    with open(info_file, 'r') as f:
        info = json.load(f)
    if not(os.path.exists('updates.json')):
        os.system('touch updates.json')
        os.system('echo {0}{1} > updates.json'.format(
                '{',
                '}'
            )
        )
    else:
        with open('updates.json', 'r') as f: 
            updates = json.load(f)
    
    for host in info["hosts"]:
        updates['updates'][host] = {
            "update": UPDATE_FOLDER_NAME,
            "md5": ''
        }
    
    with open('updates.json', 'w') as f: 
        json.dump(updates, f, indent=4)

def main():
    events = {}
    info = {}
    
    if len(sys.argv) == 1:
        events = build_update()
    elif sys.argv[1] == 'rewrite_updates':
        updates = {}
        with open('updates.json', 'r') as f: 
            updates = json.load(f)
        
        md5 = ''
        with open(UPDATE_FOLDER_NAME, 'rb') as f:
            data = f.read()
            md5 = hashlib.md5(data).hexdigest()
        
        for update in updates['updates']: 
            updates['updates'][update]['md5'] = md5
        
        with open('updates.json', 'w') as f: 
            json.dump(updates, f, indent=4)
    else:
        events = handle_update(sys.argv[1])
        rewrite_updates(sys.argv[1])
    
    with open('update_package/events.json', 'w') as event_file:
        json.dump(events, event_file, indent=4)

if __name__ == "__main__":  
    main()
