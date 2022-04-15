#!/usr/bin/env python3 

import json
import hashlib 


class UnknownEvent(Exception):
    def __init__(self, event):
        self.event = event
    

"""with open('test.txt', 'r') as f:
    data = f.read()
    md5 = hashlib.md5(data.encode()).hexdigest()
    
    print(md5)    
"""

def delete_update_package():
    print('Deleting update package...')
    
def check_syntax(events) -> bool:
    type_list = ("FileCopy", "ExecCommand")
    
    for event in events["Events"]:
        if not(event["EventType"] in type_list):
            raise UnknownEvent(event["EventType"])
            return False
        
    return True
        

def main():  
    events = {}
    
    with open('events.json', 'r') as events_file:
        events = json.load(events_file)
    
    if not(check_syntax(events)):
        print("bad")
    
    return
    
if __name__ == "__main__":
    try:
        main()
    except UnknownEvent as ue:
        print('Unknown EventType "{}" in events.json'.format(ue.event))
        delete_update_package()
    else:
        print("update successful")
