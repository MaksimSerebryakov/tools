#!/bin/bash

Help()
{
    echo "This script enables ssh on given hosts"
    echo
    echo "Command Line Arguments:"
    echo "      hostname or IP-address" 
    echo 
    echo "Options:"
    echo "      -h - shows this message and exit"
}

while getopts ':h' option; do
    case "$option" in
        h)  Help
            exit
            ;;
        \?) echo "Illegal option, run the script with -h option to see help page"
            exit 
            ;;
    esac
done

if [ -n "$1" ]
then
while [ -n "$1" ]
do
snmpwalk -v 2c -c ssh_enable $1 NET-SNMP-EXTEND-MIB::nsExtendOutLine.\"ssh_enable\".1
shift 
done
else
echo "Enter hostname or IP-address"
fi
