import json
import logging
from typing import Dict, Any, Union

from bson.json_util import dumps
from pymongo.collection import Collection

from lambda_helper import json_response, safe_execute

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Union[int, str, Dict[str, str]]]:
    return safe_execute(event, context, get_todos, False)


def get_todos(_request_body: Dict[str, str], todos_collection: Collection):
    todos = todos_collection.find()
    logger.debug(f"{todos=}")

    todos_json = dumps(todos)
    logger.debug(f"{todos_json=}")

    if todos_json:
        return json_response(status_code=200, body=todos_json)
    else:
        return json_response(status_code=500, body=json.dumps({"message": "Todo not found"}))
