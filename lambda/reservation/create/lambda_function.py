import uuid
from http import HTTPStatus
from typing import Dict
from common.rest.api_wrapper import RestApiWrapper, rest_response
from common.rest.helpers import get_entity_payload
from common.reservations.reservation_dao import ReservationDAO
from common.reservations.reservation import Reservation

reservation_dao: ReservationDAO = ReservationDAO()

@RestApiWrapper('rest_api.reservations.create')
def lambda_handler(event: Dict, context):
    reservation_payload = get_lambda_inputs(event)
    # Persist Reservation
    reservation_id = str(uuid.uuid4())
    reservation = Reservation(reservation_id=reservation_id,
                            reservation_user=reservation_payload.get('user_id'),
                            start=reservation_payload.get('start'),
                            end=reservation_payload.get('end'),
                            phone=reservation_payload.get('phone', None),
                            car_type=reservation_payload.get('car_type', None),
                            description=reservation_payload.get('description', None))
    user_email = reservation_payload.get('user_email')
    reservation_dao.create(reservation, user_email)
    return rest_response(status_code=HTTPStatus.CREATED , body=reservation.as_api_dict())


def get_lambda_inputs(event: Dict) -> Dict:
    reservation_payload: Dict = get_entity_payload(event=event)
    return reservation_payload