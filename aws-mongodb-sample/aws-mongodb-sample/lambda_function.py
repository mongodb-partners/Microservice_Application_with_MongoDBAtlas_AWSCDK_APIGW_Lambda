# aws_mongodb_sample/lambda_function.py
import os
from pymongo import MongoClient
import json
import boto3
import base64

#Sample URI = "mongodb://" + MongoDBusername + ":" + MongoDBpassword + "@" + MongoDBaddress + "/" + MongoDBname

# Your secret's name and region
secret_name = "ATLAS_URI"

def lambda_handler(event, context):
   
    #Set up our Client
    client = boto3.client('secretsmanager')
    
    # Calling SecretsManager
    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )
   
    #Extracting the key/value from the secret
    SECRET_STRING = get_secret_value_response['SecretString']

    client = MongoClient(host=SECRET_STRING)
   # Name of database
    db = client.sample_restaurants  
    
     # Count documents
    result = db.restaurants.count_documents({})
    

    if result:
      response =  {
          "statusCode": 200,
          "body": "Document count fetch successfully" + str(result),
          "headers":{ "content-type": "application/json"}
      }
      
      return response
      
    else:
       return "Failed to fetch document count"
