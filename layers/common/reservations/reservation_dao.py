import boto3
import copy
import os
from typing import Dict
from datetime import datetime, timezone
from functools import cached_property
from typing import Tuple, Optional, List
from common.users.user_dao import UserDAO
from common.reservations.reservation import Reservation, DbReservationAttrNames
from common.rest.exceptions import BadParameterException, KeyNotFoundException, DuplicateKeyException

DEFAULT_LIMIT=50
class ReservationDAO:
    """
    Data Access Object for Reservation database table.
    """

    def __init__(self, *,
                 table_name: str = os.getenv("RESERVATIONS_TABLE"),
                 region: str = os.getenv("AWS_REGION", default="us-east-1")):
        self._table_name = table_name
        self._region = region

    @cached_property
    def _dynamodb_client(self):
        return boto3.client('dynamodb', self._region)

    @cached_property
    def _dynamodb_resource(self):
        return boto3.resource('dynamodb', self._region)

    @cached_property
    def _dynamodb_resource_table(self):
        return self._dynamodb_resource.Table(self._table_name)

    def create(self, reservation: Reservation, user_email) -> None:
        """
        Create a new Reservation record.
        """
        if not reservation:
            raise BadParameterException(param_name="Reservation Key", details="Missing or empty Reservation")


        item = reservation.as_db_dict()
        condition_expression: str = f"attribute_not_exists({DbReservationAttrNames.RESERVATON_ID})"
        kwargs = {
            "Item": item,
            "ConditionExpression": condition_expression
        }
        try:
            self._dynamodb_resource_table.put_item(**kwargs)
            # When create reservation also update the Users table
            user_dao = UserDAO()
            old_user = user_dao.get(reservation.reservation_user, user_email)
            new_user = copy.deepcopy(old_user)
            new_user.add_reservations(reservation)
            user_dao.update(old_user, new_user)
        except self._dynamodb_client.exceptions.ConditionalCheckFailedException as e:
            print("Reservation already exists for Partition Key '%s'", reservation.reservation_id)
            raise DuplicateKeyException(partition_key="reservation_id",
                                        key="reservation_id",
                                        value=reservation.reservation_id,
                                        details=f"Reservation already exists for Partition Key")
    

    def get(self, reservation_id: str, reservation_user: str) -> Reservation:
        if not reservation_id:
            raise BadParameterException(param_name=DbReservationAttrNames.RESERVATON_ID, details="Missing or empty reservation_id")
        
        if not reservation_user:
            raise BadParameterException(param_name=DbReservationAttrNames.RESERVATON_USER, details="Missing or empty reservation_user")

        response = self._dynamodb_resource_table.get_item(
            Key={
                DbReservationAttrNames.RESERVATON_ID: reservation_id,
                DbReservationAttrNames.RESERVATON_USER: reservation_user
            }
        )
        item = response.get("Item")
        if not item:
            # Raise exception
            raise KeyNotFoundException(
                partition_key="reservation_id", key=DbReservationAttrNames.RESERVATON_ID, value=reservation_id,
                details=f"No Reservation was found for Partition Key reservation_id and reservation_user")

        return Reservation.from_db_dict(db_item=item)
    

    def update(self, old_reservation: Reservation, new_reservation: Reservation) -> Reservation:
        if not old_reservation:
            raise BadParameterException(param_name=DbReservationAttrNames.RESERVATON_ID, details="Missing or empty old Reservation Value")
        if not new_reservation:
            raise BadParameterException(param_name=DbReservationAttrNames.RESERVATON_ID, details="Missing or empty new Reservation Value")

        # Check what actually needs to be updated
        phone_changed: bool = old_reservation.phone != new_reservation.phone
        car_type_changed: bool = old_reservation.car_type != new_reservation.car_type
        start_changed: bool = old_reservation.start != new_reservation.start
        end_changed: bool = old_reservation.end != new_reservation.end

        # If nothing to update, return early
        if not phone_changed and not car_type_changed and not start_changed and not end_changed:
            print("Skipping update because there is nothing to update for Reservation Id '%s', Reservation user '%s'",
                new_reservation.reservation_id, new_reservation.reservation_user)
            return new_reservation

        # Check that a row with the Reservation Id and Reservation user Key already exists
        condition_expression: str = f"attribute_exists({DbReservationAttrNames.RESERVATON_ID}) AND " \
                                    f"attribute_exists({DbReservationAttrNames.RESERVATON_USER})"

        
        time = datetime.now()
        modified: str = time.astimezone(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        update_expression: str = f"SET {DbReservationAttrNames.MODIFIED}=:modified"
        expression_attribute_values: Dict = {
            ":modified": modified
        }

        if car_type_changed:
            expression_attribute_values[':car_type'] = new_reservation.car_type
            update_expression += ", car_type=:car_type"
        if phone_changed:
            expression_attribute_values[':phone'] = new_reservation.phone
            update_expression += ", phone=:phone"
        if start_changed:
            expression_attribute_values[':start'] = new_reservation.start
            update_expression += ", start=:start"
        if end_changed:
            expression_attribute_values[':end'] = new_reservation.end
            update_expression += ", end=:end"

        kwargs = {
            "Key": {
                DbReservationAttrNames.RESERVATON_ID: new_reservation.reservation_id,
                DbReservationAttrNames.RESERVATON_USER: new_reservation.reservation_user
            },
            'ConditionExpression': condition_expression,
            "UpdateExpression": update_expression,
            "ExpressionAttributeValues": expression_attribute_values,
            "ReturnValues": "ALL_NEW"
        }

        response = self._dynamodb_resource_table.update_item(**kwargs)

        item = response.get("Attributes")
        if not item:
            print("No Value was found for Reservation Id '%s', Reservation User '%s'",
                             new_reservation.reservation_id, new_reservation.reservation_user)
            raise KeyNotFoundException(
                partition_key="reservation_id", key=DbReservationAttrNames.RESERVATON_ID, value=new_reservation.reservation_id,
                details=f"No Reservation was found for Partition Key reservation_id and reservation_user")

        return Reservation.from_db_dict(db_item=item)
    

    def set(self, reservation: Reservation) -> Tuple[Reservation, bool]:
        if not reservation.reservation_id:
            raise BadParameterException(param_name=DbReservationAttrNames.RESERVATON_ID, details="Missing or empty reservation_id")
        
        if not reservation.reservation_user:
            raise BadParameterException(param_name=DbReservationAttrNames.RESERVATON_USER, details="Missing or empty reservation_user")

        try:
            old_reservation: Reservation = self.get(reservation_id=reservation.reservation_id, reservation_user=reservation.reservation_user)
        except KeyNotFoundException:
            # Reservation Values does not exist, fire create
            self.create(reservation=reservation)
            return reservation, True

        # Reservation exists, fire update
        return self.update(old_reservation=old_reservation, new_reservation=reservation), False