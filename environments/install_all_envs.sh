#!/bin/bash


update=TRUE

# get all the env files
env_files=(find . -name "*.yaml" -not -path "*/envs/*" -not -path "*/environments/*")
# read the first line of each env file to get the env name, and create the env
for env_file in "${env_files[@]}"; do
    env_name=$(head -n 1 "$env_file" | cut -d: -f2 | tr -d ' ')
    echo "Creating environment: $env_name from file: $env_file"
    if conda env list | grep -q "$env_name"; then
        echo "Environment $env_name already exists. Skipping creation."
    elif [ "$update" = "TRUE" ]; then
        echo "Environment $env_name already exists. Updating environment from file: $env_file"
        conda env update -n "$env_name" --file "$env_file" --present
    else
        echo "Environment $env_name does not exist. Creating environment from file: $env_file"
        conda env create -f "$env_file"
    fi

    cd ../utils/ || exit ; conda activate "$env_name"
    pip install -e . ; cd ../environments/ || exit
done
