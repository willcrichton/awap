#!/bin/bash
if [[ -n "$VIRTUAL_ENV" ]]; then
    python src/main.py $@
else
    echo "You need to activate virtualenv before using the server. Run:"
    echo "source venv/bin/activate"
fi
