# aws_mongodb_sample/lambda_function.py
import os
from pymongo import MongoClient
import json
import boto3
import base64
import csv

def lambda_handler(event, context):

       #Set up our Client
       client = boto3.client('secretsmanager')
       secret_name = os.environ['ATLAS_URI']

       #Calling SecretsManager
       get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
            )

       #Extracting the key/value from the secret
       ATLAS_URI = get_secret_value_response['SecretString']

       client = MongoClient(host=ATLAS_URI)

       #Create a database
       db = client["emp_data"]

       #Create a collection
       collection = db["todos"]

       # Count documents
       documents = list(collection.find({}))

       if documents:
           response =  {
              "statusCode": 200,
              "body": documents,
              "headers":{ "content-type": "application/json"}
           }

           return response

       else:
        return "Failed to fetch document count"
