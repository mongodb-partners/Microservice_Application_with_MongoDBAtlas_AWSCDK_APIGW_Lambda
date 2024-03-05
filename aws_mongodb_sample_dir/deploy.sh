#!/bin/bash

export ORG_ID="65e67d854972ac598c091461"
export MONGODB_USER="admin"
export MONGODB_PASSWORD="SuperSafePassword42!"

source .venv/bin/activate

cdk destroy --all --force

cdk bootstrap aws://722245653955/us-east-1

cdk deploy --all --require-approval never
