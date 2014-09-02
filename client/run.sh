#!/bin/bash

# TODO: remove the AI2 logic when we get server set up

RUN_AI="python python/game.py"
RUN_AI2="python ../client/python/game.py"
TEAM_ID="test"
FAST=0

trap "pkill -P $$" SIGTERM SIGKILL EXIT

while getopts "ft:" option;
do
    case $option in
        f) FAST=1 ;;
        t) TEAM_ID=$OPTARG ;;
    esac
done

if [ -f client.py ]
then
	python client.py "$RUN_AI" $TEAM_ID $FAST &
else
	python ../client/client.py "$RUN_AI2" $TEAM_ID $FAST &
fi
wait