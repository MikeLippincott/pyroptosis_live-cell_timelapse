#!/bin/bash


# expected number of dirs in the path
#################################################
# converted: 96 wells * 5 fields of view = 480
# annotated: 96 wells * 5 fields of view = 480
# annotated combined: 1
#################################################

path1="data/converted_data"
path2="data/annotated_data"
path3="data/annotated_data_combined"


# check number of subdirs
#################################################
subdirs1=$(find $path1 -type d | wc -l)
subfiles1=$(find $path1 -type f | wc -l)
subdirs2=$(find $path2 -type d | wc -l)
subfiles2=$(find $path2 -type f | wc -l)
subdirs3=$(find $path3 -type d | wc -l)
subfiles3=$(find $path3 -type f | wc -l)



if [ $subdirs1 -ne 480 ]; then
    echo "Fail: $path1 has $subdirs1 subdirs"
else
    echo "Success: $path1 has $subdirs1 subdirs"
    if [ $subfiles1 -ne 0 ]; then
        echo "Fail: $path1 has $subfiles1 files"
        for dir in "$path1"/*; do
            # check if the directory is empty
            if [ -z "$(ls -A $dir)" ]; then
                echo "Fail: $dir is empty"
            fi
        done
    else
        echo "Success: $path1 has $subfiles1 files"
    fi
fi


if [ $subdirs2 -ne 480 ]; then
    echo "Fail: $path2 has $subdirs2 subdirs"
else
    echo "Success: $path2 has $subdirs2 subdirs"
    if [ $subfiles2 -ne 0 ]; then
        echo "Fail: $path2 has $subfiles2 files"
        for dir in "$path2"/*; do
            # check if the directory is empty
            if [ -z "$(ls -A $dir)" ]; then
                echo "Fail: $dir is empty"
            fi
        done
    else
        echo "Success: $path2 has $subfiles2 files"
    fi
fi

if [ $subdirs3 -ne 1 ]; then
    echo "Fail: $path3 has $subdirs3 subdirs"
else
    echo "Success: $path3 has $subdirs3 subdirs"
    if [ $subfiles3 -ne 1 ]; then
        echo "Fail: $path3 has $subfiles3 files"
        for dir in "$path3"/*; do
            # check if the directory is empty
            if [ -z "$(ls -A $dir)" ]; then
                echo "Fail: $dir is empty"
            fi
        done
    else
        echo "Success: $path3 has $subfiles3 files"
    fi
fi
