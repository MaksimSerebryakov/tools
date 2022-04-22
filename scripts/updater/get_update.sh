#!/bin/bash

HOST=192.168.100.212
USER=maxim
PASSWORD=g64s91bx

ftp -inv $HOST <<EOF
user $USER $PASSWORD
get update_192.168.100.213.tar.gz
bye
EOF

cd update_192.168.100.213.tar.gz

if [ $? -eq 0 ]; then
echo OK
else
ftp -inv $HOST <<EOF
user $USER $PASSWORD
get update_all.tar.gz
bye
EOF
fi
