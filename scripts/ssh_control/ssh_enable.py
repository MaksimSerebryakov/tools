#!/usr/bin/env python3

import os

def enable():
    f = open('host_list', 'r')
    
    for line in f.readlines():
        line = line.split()
        os.system("./ssh_enable_hostname.sh {}".format(line[1]))
    
    f.close()

if __name__ == '__main__':
    enable()
