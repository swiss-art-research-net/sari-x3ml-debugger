# SARI X3ML Debugger

## About

This repository contains tools for debugging a X3ML Mapping file. 

The provided script takes a X3ML Mapping file and divides it into the individual mappings. The input files are then mapped using the separated mappings. A Trig file is generated that contains each mapping output in a named graph, along with the X3ML mapping that generated it.

## Usage

This is a work in progress. Currently, run using `docker-compose up -d`. 

Place the mapping file and generator policy in the `./mapping` directory and the input files in the `./input` directory. Check the paths and names in `./scripts/debug.py`

Then enter the container through `docker exec -it x3ml-debugger-jobs bash` and run the script through `python scripts/debug.py`.