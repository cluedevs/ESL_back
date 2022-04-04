from http import HTTPStatus
from typing import Dict
from common.rest.api_wrapper import RestApiWrapper, rest_response

@RestApiWrapper('rest_api.cars.getAll')
def lambda_handler(event: Dict, context):
    return rest_response(status_code=HTTPStatus.OK, body= '')