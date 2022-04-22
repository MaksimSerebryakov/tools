#!/bin/bash 

cp /home/maxim/update_192.168.100.213.tar.gz /home/maxim/tools/scripts/updater/
cd /home/maxim/tools/scripts/updater
mkdir update_package
tar -xvf update_192.168.100.213.tar.gz
cp update_192.168.100.213/* update_package
rm -rf update_192.168.100.213
rm update_192.168.100.213.tar.gz
