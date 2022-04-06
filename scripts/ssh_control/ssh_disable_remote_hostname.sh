#!/bin/bash

Help()
{
    echo "This script disables ssh on given hosts"
    echo
    echo "Command Line Arguments:"
    echo "      host username and hostname or IP-address" 
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

name=''

if [ -n "$1" ]
then
while [ -n "$1" ]
do
user=$1
shift
ssh $user@$1 /home/$user/scripts/ssh_disable.py
shift
done
else
echo "Enter host username and hostname or IP-address"
fi
