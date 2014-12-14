#!/bin/bash 

template_path=$1

find $template_path -type f -exec sed -i 's#/theme/#/static/#g' '{}' \;
