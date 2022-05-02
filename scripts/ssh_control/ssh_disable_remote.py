#!/usr/bin/env python3

import os
import sys

def disable():
    f = open('/etc/hosts', 'r')
    
    for line in f.readlines():
        line = line.split()
        os.system("./ssh_disable_remote_hostname.sh {0} {1}".format(sys.argv[1], line[1]))
    
    f.close()

if __name__ == '__main__':
    disable()
