#!/usr/bin/env python3

import os

def disable():
    f = open('host_list', 'r')
    
    for line in f.readlines():
        line = line.split()
        os.system("./ssh_disable_remote_hostname.sh {0} {1}".format(line[0], line[1]))
    
    f.close()

if __name__ == '__main__':
    disable()
