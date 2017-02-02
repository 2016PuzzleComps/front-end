#!/bin/bash

python3 puzzle_server.py cmc307-01.mathcs.carleton.edu 5001 &

pid=$!

while true; do
    sleep 5400 # sleep for 6 hours
    kill $pid
    echo "restarting"
    python3 puzzle_server.py cmc307-01.mathcs.carleton.edu 5001 &
    pid=$!
done
