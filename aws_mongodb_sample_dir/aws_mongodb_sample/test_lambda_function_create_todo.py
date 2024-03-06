import json
import os
import unittest
from typing import Dict, Any
from unittest.mock import patch, MagicMock

# Set the environment variable
os.environ["ATLAS_URI"] = "foo"

# Import the lambda function
from aws_mongodb_sample_dir.aws_mongodb_sample import lambda_function_create_todo


class TestLambdaFunctionCreateTodo(unittest.TestCase):

    @patch("lambda_helper.client")
    @patch("lambda_helper.MongoClient")
    def test_lambda_function_create_todo(self, mock_mongo_client, mock_boto3_client):
        # Create a mock boto3 client
        mock_secrets_manager = MagicMock()
        mock_boto3_client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {"SecretString": "mock_connection_string"}

        # Create a mock MongoClient
        mock_mongo_client_instance = MagicMock()
        mock_mongo_client.return_value = mock_mongo_client_instance
        mock_database = MagicMock()
        mock_collection = MagicMock()
        mock_mongo_client_instance.__getitem__.side_effect = [mock_database, mock_collection]

        # Prepare the event
        body = '{\"text\": \"TODO text\"}'
        event: Dict[str, Any] = {"body": body}

        # Call the lambda handler function
        response = lambda_function_create_todo.lambda_handler(event, None)

        # Assertions
        self.assertEqual(response["statusCode"], 201)
        self.assertIn("inserted_id", json.loads(response["body"])["id"])


if __name__ == "__main__":
    unittest.main()
