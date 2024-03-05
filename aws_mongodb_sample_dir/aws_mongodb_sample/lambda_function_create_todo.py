import os

import boto3
from pymongo import MongoClient


def lambda_handler(event, context):
    secrets_manager = boto3.client('secretsmanager')
    secret_name = os.environ['ATLAS_URI']
    secret_value_response = secrets_manager.get_secret_value(SecretId=secret_name)
    connection_string = secret_value_response['SecretString']

    mongo_client = MongoClient(host=connection_string)
    app_database = mongo_client["app"]
    todos_collection = app_database["todos"]

    todo_id = event['pathParameters']['id']

    result = todos_collection.delete_one({"_id": todo_id})

    if result.deleted_count > 0:
        response = {
            "statusCode": 200,
            "body": "Todo deleted successfully",
            "headers": {"Content-Type": "application/json"}
        }
    else:
        response = {
            "statusCode": 404,
            "body": "Todo not found",
            "headers": {"Content-Type": "application/json"}
        }

    return response
