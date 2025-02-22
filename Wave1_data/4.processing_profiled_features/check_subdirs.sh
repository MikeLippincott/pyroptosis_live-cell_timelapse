#!/bin/bash


# expected number of dirs in the path
#################################################
# analysis_output: 480
# converted: 96 wells * 5 fields of view = 480
# annotated: 96 wells * 5 fields of view = 480
# annotated combined: 1
#################################################

path0="../2.illumination_correction/illum_directory"
path1="../3.cellprofiling/analysis_output"
path2="data/converted_data"
path3="data/annotated_data"
path4="data/annotated_data_combined"


# check number of subdirs
#################################################
subdirs0=$(find $path0 -type d | wc -l)
subfiles0=$(find $path0 -type f | wc -l)
subdirs1=$(find $path1 -type d | wc -l)
subfiles1=$(find $path1 -type f | wc -l)
subdirs2=$(find $path2 -type d | wc -l)
subfiles2=$(find $path2 -type f | wc -l)
subdirs3=$(find $path3 -type d | wc -l)
subfiles3=$(find $path3 -type f | wc -l)
subdirs4=$(find $path4 -type d | wc -l)
subfiles4=$(find $path4 -type f | wc -l)

if [ $subdirs0 -ne 480 ]; then
    echo "Fail: $path0 has $subdirs0 subdirs"
    if [ $subfiles0 -ne 0 ]; then
        echo "Fail: $path0 has $subfiles0 files"
        for dir in "$path0"/*; do
            # check if the directory is empty
            if [ -z "$(ls -A $dir)" ]; then
                echo "Fail: $dir is empty"
            fi
        done
    fi
else
    echo "Success: $path0 has $subdirs0 subdirs"

fi

if [ $subdirs1 -ne 480 ]; then
    echo "Fail: $path1 has $subdirs1 subdirs"
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
else
    echo "Success: $path1 has $subdirs1 subdirs"

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

if [ $subdirs3 -ne 480 ]; then
    echo "Fail: $path3 has $subdirs3 subdirs"
else
    echo "Success: $path3 has $subdirs3 subdirs"
    if [ $subfiles3 -ne 0 ]; then
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



if [ $subdirs4 -ne 1 ]; then
    echo "Fail: $path4 has $subdirs4 subdirs"
else
    echo "Success: $path4 has $subdirs4 subdirs"
    if [ $subfiles4 -ne 1 ]; then
        echo "Fail: $path4 has $subfiles4 files"
        for dir in "$path4"/*; do
            # check if the directory is empty
            if [ -z "$(ls -A $dir)" ]; then
                echo "Fail: $dir is empty"
            fi
        done
    else
        echo "Success: $path4 has $subfiles4 files"
    fi
fi
