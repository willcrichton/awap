#!/bin/bash

RUN_AI="python game.py"
RUN_AI2="python ../client/game.py"
TEAM_ID="test"

if [ "$1" != "" ]; then
    TEAM_ID=$1
fi

if [ -f client.py ]
then
	python client.py "$RUN_AI" $TEAM_ID
else
	python ../client/client.py "$RUN_AI2" $TEAM_ID
fi