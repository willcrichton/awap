#!/bin/bash

RUN_AI="python game.py"
TEAM_ID="will"

if [ "$1" != "" ]; then
    TEAM_ID=$1
fi

python client.py "$RUN_AI" $TEAM_ID
