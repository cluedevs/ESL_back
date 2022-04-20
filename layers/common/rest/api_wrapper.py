import json
from typing import Dict
from http import HTTPStatus
from common.rest.exceptions import generate_api_error_body, RestException, AbstractException, DatabaseException, KeyNotFoundException, NotPermittedException


def rest_response(status_code: int, body: Dict = None, headers: Dict = None) -> Dict:
    """
    Builds an API Gateway-compatible REST response for a Lambda.
    """

    response: Dict = {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body)
    if headers is not None:
        response['headers'].update(headers)
    return response

class RestApiWrapper:
    """
    This decorator wraps API Gateway Lambdas, intercepting known error types
    and converting them to strongly typed errors. Unknown error types will be
    converted to 500s.
    """
    def __init__(self, endpoint_name):
        self.endpoint_name = endpoint_name

    def __call__(self, func):
        def do_wrap(event, context):
            # pylint: disable=too-many-return-statements
            print(f"Endpoint:{self.endpoint_name} , Event: {event}")
            try:
                return func(event, context)
            # Errors raised by common code
            except KeyNotFoundException as e:
                return rest_response(status_code=HTTPStatus.NOT_FOUND,
                                     body=generate_api_error_body(
                                         http_status=HTTPStatus.NOT_FOUND,
                                         message='Not Found',
                                         details=f"Value with key '{e.value}' not found.' "))
            except NotPermittedException as e:
                print("Handling not permitted error")
                return rest_response(status_code=HTTPStatus.FORBIDDEN,
                                     body=generate_api_error_body(
                                         http_status=HTTPStatus.FORBIDDEN,
                                         message='Operation not permitted',
                                         details=str(e)))
            except DatabaseException as e:
                # Unknown database error related to state of DynamoDB itself or the state of the data returned by it
                return rest_response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                     body=generate_api_error_body(
                                         http_status=HTTPStatus.INTERNAL_SERVER_ERROR,
                                         message='Internal Server Error',
                                         details=str(e)))
            except AbstractException as e:
                return rest_response(status_code=HTTPStatus.BAD_REQUEST,
                                     body=generate_api_error_body(
                                         http_status=HTTPStatus.BAD_REQUEST,
                                         message='Bad Request',
                                         details=str(e)))
            # Errors raised by REST code
            except RestException as e:
                print("Handling rest error")
                return rest_response(e.http_status, e.to_api_error())
            except Exception as e:
                print("Unexpected exception")
                return rest_response(
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    generate_api_error_body(HTTPStatus.INTERNAL_SERVER_ERROR, "Internal Server Error", str(e)))

        return do_wrap
