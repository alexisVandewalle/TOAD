#!/bin/bash

source venv/bin/activate
cd client
export FLASK_APP=webapp
export FLASK_ENV=development
flask run
