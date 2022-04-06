#!/usr/bin/env python3

"""SSH-Disabler.

Disable ssh on this unit and disconnect all users connected via ssh.
"""

import os
import sys
import argparse

def find_ssh_users():
    os.system("touch ./ssh_connections.txt")
    os.system("sudo lsof -n -a -itcp -stcp:established -c sshd > ./ssh_connections.txt")

def parse_ssh_connections():
    f = open('ssh_connections.txt', 'r')
    
    connections = list()
    
    for line in f.readlines():
        if line.split()[0] == 'sshd':
            connections.append(line)
    
    f.close()
    
    return connections

def disable_ssh():
    os.system("sudo systemctl stop ssh")
    os.system("sudo systemctl disable ssh")

def disconnect_users():
    find_ssh_users()
    connections = parse_ssh_connections()
    
    for line in connections:
        line = line.split()
        
        #if line[8].split('->')[1].split(':')[0] in addresses:
        os.system("sudo kill -9 {}".format(line[1]))

    os.system("rm ssh_connections.txt")


def main():
    """Main Function"""
    
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__)
    parser.parse_args()
    
    disable_ssh()
    disconnect_users()
    
    
if __name__ == '__main__':
    main()
    
