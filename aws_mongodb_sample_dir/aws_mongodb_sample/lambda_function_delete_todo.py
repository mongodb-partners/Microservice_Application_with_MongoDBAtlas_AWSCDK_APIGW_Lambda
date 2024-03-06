import json
import logging
from typing import Dict, Any, Union

from bson import ObjectId
from pymongo.collection import Collection

from lambda_helper import json_response, safe_execute

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Union[int, str, Dict[str, str]]]:
    return safe_execute(event, context, delete_todo, True)


def delete_todo(request_body: Dict[str, str], todos_collection: Collection):
    if "id" not in request_body:
        return json_response(status_code=400, body=json.dumps({"message": "Missing id in request body"}))

    id_str = request_body["id"]
    logger.debug(f"{id_str=}")

    oid = ObjectId(id_str)
    logger.debug(f"{oid=}")

    result = todos_collection.delete_one({"_id": oid})
    logger.debug(f"{result=}")

    if result.deleted_count > 0:
        return json_response(status_code=200, body=json.dumps({"message": "Todo deleted successfully"}))
    else:
        return json_response(status_code=500, body=json.dumps({"message": "Todo not found"}))
