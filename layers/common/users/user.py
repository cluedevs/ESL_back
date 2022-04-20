import uuid
from dataclasses import dataclass
from typing import Optional, Dict
from datetime import datetime, timezone
from common.rest.exceptions import BadParameterException


class DbUserAttrNames():
    """
    Database Attribute names to be used for Users table.
    """
    USER_ID = 'user_id'
    USER_EMAIL = 'user_email'
    MODIFIED = 'modified'

@dataclass(init=False)
class User:
    """
    Encapsulates the representation of a User.
    """
    user_id : str
    user_email: str
    name: str
    age: int
    created: str
    modified: str

    def __init__(self, user_id: str, user_email: str, name: Optional[str] = None, age: Optional[int] = None, created: Optional[str] = None, modified: Optional[str] = None):
        if not user_id:
            raise BadParameterException(param_name="user_id",
                                        details='key must be provided')
        if not user_email:
            raise BadParameterException(param_name="user_email",
                                        details='key must be provided')
        self.user_id = user_id
        self.user_email = user_email
        self.name = name
        self.age = age

        if not created:
            time = datetime.now()
            created = time.astimezone(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
            modified = created

        self.created = created
        self.modified = modified
        self.created = created
        self.modified = modified

    def as_db_dict(self) -> Dict:
        """Returns a dict that can be serialized as JSON to store in database"""
        user_dict: Dict = {
            DbUserAttrNames.USER_ID: self.user_id,
            DbUserAttrNames.USER_EMAIL: self.user_email
        }

        if self.name:
            user_dict['name'] = self.name

        if self.age:
            user_dict['age'] = self.age

        if self.created:
            user_dict['created'] = self.created

        if self.modified:
            user_dict['modified'] = self.modified

        return user_dict

    @classmethod
    def from_db_dict(cls, db_item: dict):
        """Returns the User instance populated from the database dict"""
        user_id = db_item.get(DbUserAttrNames.USER_ID)
        user_email = db_item.get(DbUserAttrNames.USER_EMAIL)
        name = db_item.get("name")
        age = db_item.get("age")
        created = db_item.get("created")
        modified = db_item.get("modified")

        return cls(user_id=user_id,
                    user_email=user_email,
                    name=name,
                    age=age,
                    created=created,
                    modified=modified)