import json
import logging
from typing import Dict, Any, Union

from pymongo.collection import Collection
from pymongo.results import InsertOneResult

from lambda_helper import json_response, safe_execute

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Union[int, str, Dict[str, str]]]:
    return safe_execute(event, context, create_todo, True)


def create_todo(request_body: Dict[str, str], todos_collection: Collection):
    todo_text: str = request_body["text"]
    logger.debug(f"{todo_text=}")

    todo: Dict[str, str] = {"text": todo_text}
    logger.debug(f"{todo=}")

    result: InsertOneResult = todos_collection.insert_one(todo)
    logger.debug(f"{result=}")

    if result.inserted_id:
        inserted_id = str(result.inserted_id)
        logger.debug(f"{inserted_id=}")
        return json_response(status_code=201, body=json.dumps({"id": inserted_id}))
    else:
        return json_response(status_code=500, body=json.dumps({"message": "Failed to create TODO!"}))
