from http import HTTPStatus
from typing import Dict, Tuple
from common.rest.api_wrapper import RestApiWrapper, rest_response
from common.rest.helpers import get_path_param, get_entity_payload
from common.users.user_dao import UserDAO
from common.users.user import User

user_dao: UserDAO = UserDAO()

@RestApiWrapper('rest_api.users.update')
def lambda_handler(event: Dict, context):
    user_payload, user_id = get_lambda_inputs(event)
    # Persist User
    user = User(user_id, user_payload.get('user_email'), user_payload.get('name', None) , user_payload.get('age', None))
    persisted_user, is_create = user_dao.set(user)
    return rest_response(status_code=HTTPStatus.CREATED if is_create else HTTPStatus.OK,
                         body=persisted_user.as_api_dict())

def get_lambda_inputs(event: Dict) -> Tuple[Dict, str]:
    user_payload: Dict = get_entity_payload(event=event)
    user_id: str = get_path_param(event=event, path_param_name='userId')
    return user_payload, user_id