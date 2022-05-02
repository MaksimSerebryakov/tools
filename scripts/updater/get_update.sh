#!/bin/bash

HOST=192.168.100.212
USER=anonymous
PASSWORD="\n"
hostname=$(hostname)

ftp -inv $HOST <<EOF
user $USER $PASSWORD
lcd /home/maxim/updater
cd pub
get updates.json
bye
EOF

cd /home/maxim/updater

file=$(python3 -c "import json; f = open('updates.json', 'r'); print(json.load(f)['updates']['$hostname']['update']); f.close()")
md5=$(python3 -c "import json; f = open('updates.json', 'r'); print(json.load(f)['updates']['$hostname']['md5']); f.close()")

ftp -inv $HOST <<EOF
user $USER $PASSWORD
lcd /home/maxim/updater
cd pub
get $file
bye
EOF

md5cur=($(md5sum $file))
echo $md5cur $md5

if [[ $md5 != $md5cur ]]
then
echo file $file is broken
rm -rf update_package/
rm $file
rm updates.json
else 
echo $file is ok
fi
