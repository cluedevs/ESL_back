import uuid
from dataclasses import dataclass
from typing import Optional, Dict
from datetime import datetime, timezone
from common.rest.exceptions import BadParameterException


class DbReservationAttrNames():
    """
    Database Attribute names to be used for Reservations table.
    """
    RESERVATON_ID = 'reservation_id'
    RESERVATON_USER = 'reservation_user'
    START = 'start'
    END = 'end'
    MODIFIED = 'modified'
    CREATED = 'created'

@dataclass(init=False)
class Reservation:
    """
    Encapsulates the representation of a Reservation.
    """
    reservation_id : str
    reservation_user: str
    start: str
    end: str
    phone: str
    car_type: str
    description: str
    created: str
    modified: str

    def __init__(self, reservation_id: str, reservation_user: str, start: str, end: str, phone: Optional[str] = None, car_type: Optional[int] = None, description: Optional[str] = None, created: Optional[str] = None, modified: Optional[str] = None):
        if not reservation_id:
            raise BadParameterException(param_name="reservation_id",
                                        details='key must be provided')
        if not reservation_user:
            raise BadParameterException(param_name="reservation_user",
                                        details='key must be provided')
        if not start:
            raise BadParameterException(param_name="start",
                                        details='key must be provided')
        if not end:
            raise BadParameterException(param_name="end",
                                        details='key must be provided')
        self.reservation_id = reservation_id
        self.reservation_user = reservation_user
        self.start = start
        self.end = end
        self.phone = phone
        self.car_type = car_type
        self.description = description
        if not created:
            time = datetime.now()
            created = time.astimezone(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
            modified = created
        self.created = created
        self.modified = modified


    def as_db_dict(self) -> Dict:
        """Returns a dict that can be serialized as JSON to store in database"""
        reservation_dict: Dict = {
            DbReservationAttrNames.RESERVATON_ID: self.reservation_id,
            DbReservationAttrNames.RESERVATON_USER: self.reservation_user,
            DbReservationAttrNames.START: self.start,
            DbReservationAttrNames.END: self.end
        }

        if self.phone:
            reservation_dict['phone'] = self.phone

        if self.car_type:
            reservation_dict['car_type'] = self.car_type
        
        if self.description:
            reservation_dict['description'] = self.description

        if self.created:
            reservation_dict['created'] = self.created

        if self.modified:
            reservation_dict['modified'] = self.modified

        return reservation_dict


    @classmethod
    def from_db_dict(cls, db_item: dict):
        """Returns the Reservation instance populated from the database dict"""
        reservation_id = db_item.get(DbReservationAttrNames.RESERVATON_ID)
        reservation_user = db_item.get(DbReservationAttrNames.RESERVATON_USER)
        start = db_item.get(DbReservationAttrNames.START)
        end = db_item.get(DbReservationAttrNames.END)
        phone = db_item.get("phone")
        car_type = db_item.get("car_type")
        description = db_item.get("description")
        created = db_item.get("created")
        modified = db_item.get("modified")

        return cls(reservation_id=reservation_id,
                    reservation_user=reservation_user,
                    start=start,
                    end=end,
                    phone=phone,
                    car_type=car_type,
                    description=description,
                    created=created,
                    modified=modified)
    

    def as_api_dict(self) -> Dict:
        """Returns a dict that can be serialized as JSON to return in api"""
        reservation: Dict = {
            DbReservationAttrNames.RESERVATON_ID: self.reservation_id,
            DbReservationAttrNames.RESERVATON_USER: self.reservation_user,
            DbReservationAttrNames.START: self.start,
            DbReservationAttrNames.END: self.end,
            'phone': self.phone,
            'car_type': self.car_type,
            'description': self.description,
            DbReservationAttrNames.CREATED: self.created,
            DbReservationAttrNames.MODIFIED: self.modified
        }
        return reservation