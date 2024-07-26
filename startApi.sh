#! usr/bin/bash
source ./venv/bin/activate
cd ./Source
uvicorn webApi:app --host 0.0.0.0 --port 8080