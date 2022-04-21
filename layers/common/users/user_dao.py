import boto3
import os
from typing import Dict, Optional
from datetime import datetime, timezone
from functools import cached_property
from typing import Tuple
from common.users.user import User, DbUserAttrNames
from common.rest.exceptions import BadParameterException, KeyNotFoundException, DuplicateKeyException

class UserDAO:
    """
    Data Access Object for User database table.
    """

    def __init__(self, *,
                 table_name: str = os.getenv("USERS_TABLE"),
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

    def create(self, user: User) -> None:
        """
        Create a new User record.
        """
        if not user:
            raise BadParameterException(param_name="User kEY", details="Missing or empty User")


        item = user.as_db_dict()
        condition_expression: str = f"attribute_not_exists({DbUserAttrNames.USER_ID}) AND " \
                                    f"attribute_not_exists({DbUserAttrNames.USER_EMAIL})"

        kwargs = {
            "Item": item,
            "ConditionExpression": condition_expression
        }
        try:
            self._dynamodb_resource_table.put_item(**kwargs)
        except self._dynamodb_client.exceptions.ConditionalCheckFailedException as e:
            print("User already exists for Partition Key '%s' and Sort Key '%s'",
                             user.user_id, user.user_email)
            raise DuplicateKeyException(partition_key="user_id",
                                        key="user_email",
                                        value=user.user_email,
                                        details=f"User already exists for Partition Key")
    
    def get(self, user_id: str, user_email: Optional[str] = None) -> User:
        if not user_id:
            raise BadParameterException(param_name=DbUserAttrNames.USER_ID, details="Missing or empty user_id")

        args = {
            DbUserAttrNames.USER_ID: user_id
        }
        if user_email:
            args[DbUserAttrNames.USER_EMAIL] = user_email

        response = self._dynamodb_resource_table.get_item(
            Key=args
        )
        item = response.get("Item")
        if not item:
            # Raise exception
            raise KeyNotFoundException(
                partition_key="user_id", key=DbUserAttrNames.USER_ID, value=user_email,
                details=f"No User was found for Partition Key user_id and user_email")

        return User.from_db_dict(db_item=item)
    
    def update(self, old_user: User, new_user: User) -> User:
        if not old_user:
            raise BadParameterException(param_name=DbUserAttrNames.USER_ID, details="Missing or empty old User Value")
        if not new_user:
            raise BadParameterException(param_name=DbUserAttrNames.USER_ID, details="Missing or empty new User Value")

        # Check what actually needs to be updated
        age_changed: bool = old_user.age != new_user.age
        name_changed: bool = old_user.name != new_user.name
        # TODO: Only work for add or remove reservations not to modify it
        reservations_changed: bool = len(old_user.reservations) != len(new_user.reservations)

        # If nothing to update, return early
        if not age_changed and not name_changed and not reservations_changed:
            print("Skipping update because there is nothing to update for User Id '%s', User email '%s'",
                new_user.user_id, new_user.user_email)
            return new_user

        # Check that a row with the User Id and User email Key already exists
        condition_expression: str = f"attribute_exists({DbUserAttrNames.USER_ID}) AND " \
                                    f"attribute_exists({DbUserAttrNames.USER_EMAIL})"

        
        time = datetime.now()
        modified: str = time.astimezone(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        update_expression: str = f"SET {DbUserAttrNames.MODIFIED}=:modified"
        expression_attribute_values: Dict = {
            ":modified": modified
        }

        if name_changed:
            expression_attribute_values[':name'] = new_user.name
            update_expression += ", name=:name"
        if age_changed:
            expression_attribute_values[':age'] = new_user.age
            update_expression += ", age=:age"
        if reservations_changed:
            expression_attribute_values[':reservations'] = new_user.reservations
            update_expression += ", reservations=:reservations"

        kwargs = {
            "Key": {
                DbUserAttrNames.USER_ID: new_user.user_id,
                DbUserAttrNames.USER_EMAIL: new_user.user_email
            },
            'ConditionExpression': condition_expression,
            "UpdateExpression": update_expression,
            "ExpressionAttributeValues": expression_attribute_values,
            "ReturnValues": "ALL_NEW"
        }

        response = self._dynamodb_resource_table.update_item(**kwargs)

        item = response.get("Attributes")
        if not item:
            print("No Value was found for User Id '%s', User Email '%s'",
                             new_user.user_id, new_user.user_email)
            raise KeyNotFoundException(
                partition_key="user_id", key=DbUserAttrNames.USER_EMAIL, value=new_user.user_email,
                details=f"No User was found for Partition Key user_id and user_email")

        return User.from_db_dict(db_item=item)
    
    def set(self, user: User) -> Tuple[User, bool]:
        if not user.user_id:
            raise BadParameterException(param_name=DbUserAttrNames.USER_ID, details="Missing or empty user_id")
        
        if not user.user_email:
            raise BadParameterException(param_name=DbUserAttrNames.USER_EMAIL, details="Missing or empty user_email")

        try:
            old_user: User = self.get(user_id=user.user_id, user_email=user.user_email)
        except KeyNotFoundException:
            # User Values does not exist, fire create
            self.create(user=user)
            return user, True

        # User exists, fire update
        return self.update(old_user=old_user, new_user=user), False

