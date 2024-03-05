import json
import os

import boto3
from pymongo import MongoClient


def lambda_handler(event, context):
    print("Incoming event:", json.dumps(event))  # Add this line for debugging

    try:
        # Extract todo id from the request body
        request_body = json.loads(event['body'])
        todo_id = request_body['id']
    except KeyError as e:
        error_response = {
            "statusCode": 400,
            "body": json.dumps({"message": "Missing required parameter: id"})
        }
        return error_response

    # Retrieve the connection string from Secrets Manager
    secrets_manager = boto3.client('secretsmanager')
    secret_name = os.environ['ATLAS_URI']
    secret_value_response = secrets_manager.get_secret_value(SecretId=secret_name)
    connection_string = secret_value_response['SecretString']

    # Connect to MongoDB
    mongo_client = MongoClient(host=connection_string)
    app_database = mongo_client["app"]
    todos_collection = app_database["todos"]

    # Delete the todo from the collection
    result = todos_collection.delete_one({"_id": todo_id})

    # Check if the todo was successfully deleted
    if result.deleted_count > 0:
        # Return success response
        response = {
            "statusCode": 200,
            "body": "Todo deleted successfully",
            "headers": {"Content-Type": "application/json"}
        }
    else:
        # Return not found response if the todo doesn't exist
        response = {
            "statusCode": 404,
            "body": "Todo not found",
            "headers": {"Content-Type": "application/json"}
        }

    return response
