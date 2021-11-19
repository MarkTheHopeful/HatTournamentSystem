#!/usr/bin/env bash

# You should run this inside a tmux session

export FLASK_APP=hts_server.py
flask run --host=0.0.0.0 --port=22421 &> .hts_server.log

# And then leave the session using ^-B d
# TODO: Make the whole app start process run using just one (this) script