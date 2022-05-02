#!/bin/bash 

hostname=$(hostname)
file=$(python3 -c "import json; f = open('/home/maxim/updater/updates.json', 'r'); print(json.load(f)['updates']['$hostname']['update']); f.close()")

#cp /home/maxim/update_192.168.100.213.tar.gz /home/maxim/updater/
cd /home/maxim/updater
mkdir update_package
tar -xvf $file 
#cp update_192.168.100.213/* update_package
#rm -rf update_192.168.100.213
rm $file
rm updates.json

sudo ./install/install_update.py
