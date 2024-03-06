import json
import logging
import os
from typing import Dict, Any, Final, Callable

from boto3 import client
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

SECRET_NAME: Final[str] = os.environ["ATLAS_URI"]


def json_response(status_code: int, body: str) -> Dict[str, str]:
    return {
        "statusCode": status_code,
        "body": body,
        "headers": {"Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "*"
                    }
    }


def safe_execute(event: Dict[str, Any], context: Any, function: Callable[[Dict[str, str], Collection], Dict[str, str]],
                 needs_request_body: bool):
    try:
        logger.debug(f"{event=}")
        logger.debug(f"{context=}")

        request_body: Dict[str, str] = {}
        if needs_request_body:
            if "body" not in event or event["body"] is None:
                return json_response(status_code=400, body=json.dumps({"message": "Request body is missing or empty"}))

            try:
                request_body = json.loads(event["body"])
            except Exception as exception:
                logger.error(f"Error loading JSON from request body: {str(exception)}")
                return json_response(status_code=400, body=json.dumps({"message": "Invalid JSON in request body"}))

        logger.debug(f"{request_body=}")

        secrets_manager: client = client("secretsmanager")

        secret_value_response: Dict = secrets_manager.get_secret_value(SecretId=SECRET_NAME)
        connection_string: str = secret_value_response["SecretString"]

        mongo_client: MongoClient = MongoClient(host=connection_string)
        app_database: Database = mongo_client["app"]
        todos_collection: Collection = app_database["todos"]

        return function(request_body, todos_collection)

    except Exception as exception:
        logger.error(str(exception))
        return json_response(status_code=500, body=json.dumps({"message": f"Internal server error: {str(exception)}"}))
