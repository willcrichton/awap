#!/bin/bash
if [[ -n "$VIRTUAL_ENV" ]]; then
    python src/main.py $@
else
    echo "You need to activate virtualenv before using the server. I AM A CONFLICT"
    echo "source venv/bin/activate"
fi
