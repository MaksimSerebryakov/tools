#!/bin/bash

dir=$(dirname $0)
file="host_list"

for var in $(cat $file)
do 
. ${dir}/ssh_enable_hostname.sh $var
done
