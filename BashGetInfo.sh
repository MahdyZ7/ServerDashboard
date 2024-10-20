#!/bin/bash

sshpass -p $3 ssh -oHostKeyAlgorithms=+ssh-dss "$2"@"$1" "bash -s" < $4