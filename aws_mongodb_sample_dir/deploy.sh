#!/bin/bash

export ORG_ID="<ORG_ID>"
export MONGODB_USER="<MONGODB_USER>"
export MONGODB_PASSWORD="<MONGODB_PASSWORD>"

python3 -m venv .venv || true
source .venv/bin/activate
pip3 install -r requirements.txt

cd aws_mongodb_sample || exit
pip install --target ./dependencies pymongo
cd ..

cdk destroy --all --force

cdk bootstrap aws://<ACCOUNT_NUMBER>/us-east-1

cdk deploy --all --require-approval never
