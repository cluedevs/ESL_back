import json
from urllib.parse import unquote
from typing import Dict
from common.rest.exceptions import BadRequest

def get_path_param(event: Dict, path_param_name: str) -> str:
    """
    Returns the path parameter value from the event object, it should always be available in a valid request.
    Throws BadRequest Exception if a None value if not found.
    """
    param_value = (event.get('pathParameters') or {}).get(path_param_name)
    if not param_value:
        print(f'{path_param_name} not found in path parameters.')
        raise BadRequest(details=f'Path Parameter: {path_param_name} is missing or empty.')
    return unquote(param_value) 

def get_entity_payload(event: Dict) -> Dict:
    """
    Extracts the entity payload from the event's body.
    """
    try:
        return json.loads(event.get('body') ) if 'body' in event else {}
    except Exception as e:
        raise BadRequest(message="Bad Payload", details=f"Object missing from Payload: {str(e)}")
