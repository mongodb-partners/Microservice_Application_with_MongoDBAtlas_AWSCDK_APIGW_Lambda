import os

import boto3
from bson.json_util import dumps
from pymongo import MongoClient


def lambda_handler(event, context):
    # Retrieve the connection string from Secrets Manager
    secrets_manager = boto3.client('secretsmanager')
    secret_name = os.environ['ATLAS_URI']
    secret_value_response = secrets_manager.get_secret_value(SecretId=secret_name)
    connection_string = secret_value_response['SecretString']

    # Connect to MongoDB
    mongo_client = MongoClient(host=connection_string)
    app_database = mongo_client["app"]
    todos_collection = app_database["todos"]

    # Retrieve all todos from the collection
    todos = todos_collection.find()

    # Convert todos to JSON format
    todos_json = dumps(todos)

    # Check if todos exist
    if todos_json:
        # Return success response with todos
        response = {
            "statusCode": 200,
            "body": todos_json,
            "headers": {"Content-Type": "application/json"}
        }
    else:
        # Return not found response if no todos exist
        response = {
            "statusCode": 404,
            "body": "No todos found",
            "headers": {"Content-Type": "application/json"}
        }

    return response
