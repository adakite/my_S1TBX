#!/bin/bash
#
#
# A. Lucas, 2016

clear
metafile=$1
echo "Downloading Sentinel data from HHSD ESA service using" $metafile

user="username"
passwd="userpasswd"

aria2c --http-user=$user --http-passwd=$passwd --check-certificate=false --max-concurrent-downloads=2 -M $metafile
