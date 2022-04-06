#!/bin/bash

dir=$(dirname $0)
file="host_list"

for var in $(cat $file)
do
. ${dir}/ssh_disable_remote_hostname.sh $var
done
