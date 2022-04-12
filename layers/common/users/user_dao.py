import boto3
import os
from functools import cached_property
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
    
    def get(self, user_id: str, user_email: str) -> User:
        if not user_id:
            raise BadParameterException(param_name=DbUserAttrNames.USER_ID, details="Missing or empty user_id")
        
        if not user_email:
            raise BadParameterException(param_name=DbUserAttrNames.USER_EMAIL, details="Missing or empty user_email")

        response = self._dynamodb_resource_table.get_item(
            Key={
                DbUserAttrNames.USER_ID: user_id,
                DbUserAttrNames.USER_EMAIL: user_email
            }
        )
        item = response.get("Item")
        if not item:
            # Raise exception
            raise KeyNotFoundException(
                partition_key="user_id", key=DbUserAttrNames.USER_ID, value=user_email,
                details=f"No User was found for Partition Key user_id and user_email")

        return user_id.from_db_dict(db_item=item)
    
    def set(self, flag_value: FlagValue, is_privileged: bool = False) -> Tuple[FlagValue, bool]:
        if not flag_value:
            raise BadParameterException(param_name=DbAttrNames.FLAG_KEY, details="Missing or empty Flag Value")

        try:
            # Raises KeyNotFoundException if it does not exist
            old_flag_value: FlagValue = self.get(tenant_id=flag_value.tenant_id, flag_key=flag_value.flag_key,
                                                 scope=flag_value.scope)
        except KeyNotFoundException:
            # Flag Values does not exist, fire create
            self._create(flag_value=flag_value)
            return flag_value, True

        # Check if value is not locked
        if old_flag_value.locked and not is_privileged:
            raise NotPermittedException(param_names={DbAttrNames.LOCKED},
                                        details=f"Flag Value is locked for Flag Key '{flag_value.flag_key}' and "
                                                f"cannot be set")
        # Flag Values exists, fire update
        return self._update(old_flag_value=old_flag_value, new_flag_value=flag_value), False