#!/usr/bin/bash
export CONTAINER_DIR=${HOME}
docker run --rm \
       --mount type=bind,source=${CONTAINER_DIR}/MaatDafData,target=/home/mduser/MaatDafData \
       --mount type=bind,source=${CONTAINER_DIR}/MaatDafScratch,target=/home/mduser/MaatDafScratch \
       maat_daf_app --project GdasWfre --case Aug19 --experiment ctrl --start cold --spin_up -ccc
