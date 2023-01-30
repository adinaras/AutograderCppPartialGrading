#!/usr/bin/env bash

apt update
apt -y install build-essential make python3 python3-pip bats bc
pip3 install -r /autograder/source/requirements.txt