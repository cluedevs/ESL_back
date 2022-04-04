from http import HTTPStatus
from typing import Optional ,Set

def generate_api_error_body(http_status, message, details=None):
    api_error = {
        'code': http_status,
        'message': message,
    }
    if details:
        api_error['details'] = details
    return api_error


class RestException(Exception):
    """
    A generic exception type that will be caught by RestApiErrorHandler and
    converted to a user-facing error message.
    """
    def __init__(self, http_status: int, message: str, details: Optional[str]) -> None:
        super().__init__(details)
        self.http_status = http_status
        self.message = message
        self.details = details

    def to_api_error(self):
        """
        Converts error into something more useful for clients.
        """
        return generate_api_error_body(self.http_status, self.message, self.details)


class BadRequest(RestException):
    """
    Thrown when there is a problem with the data provided by the client.
    """
    def __init__(self, message: str = 'Bad Request', details: Optional[str] = None) -> None:
        super().__init__(HTTPStatus.BAD_REQUEST, message, details)


class Forbidden(RestException):
    """
    Thrown when the request is not permitted.
    """
    def __init__(self, message: str, details: Optional[str] = None) -> None:
        super().__init__(HTTPStatus.FORBIDDEN, message, details)


class AbstractException(Exception):
    pass


class BadParameterException(AbstractException):
    def __init__(self, param_name: str, details: str = "") -> None:
        self.param_name = param_name
        self.details = details

        super().__init__(f"Bad parameter '{param_name}': {details}")


class ValidationException(AbstractException):
    def __init__(self, param_names: Set[str], details: str = "") -> None:
        self.param_names = param_names
        self.details = details

        super().__init__(f"Validation error on parameters {param_names}: {details}")


class NotPermittedException(AbstractException):
    def __init__(self, param_names: Set[str], details: str = "") -> None:
        self.param_names = param_names
        self.details = details

        super().__init__(f"Not permitted error on parameters {param_names}: {details}")


class KeyException(AbstractException):
    """A generic error that is raised for all errors related to dynamo db keys when none of the sub-classes apply."""
    def __init__(self, partition_key: str, key: str, value: str, details: str) -> None:
        """
        :param partition_key: The partition key
        :param key: The name of the key, typically one of the API names for id, pk1, and externalId
        :param value: The value of the key that resulted in this error
        :param details: A message describing the exception. If one is not specified, a generic message will be
        generated.
        """
        self.partition_key = partition_key
        self.key = key
        self.value = value
        self.details = details or f'An error occurred for item with key {key}={value}, partition_key={partition_key}'
        super().__init__(self.details)


class DuplicateKeyException(KeyException):
    def __init__(self, partition_key: str, key: str, value: str, details: str = None) -> None:
        super().__init__(partition_key, key, value, details
                         or f'Duplicate key error for key {key}={value}, partition_key={partition_key}')


class KeyNotFoundException(KeyException):
    def __init__(self, partition_key: str, key: str, value: str, details: str = None) -> None:
        super().__init__(partition_key, key, value, details
                         or f'No record found for key {key}={value}, partition_key={partition_key}')


class DatabaseException(AbstractException):
    """Generic error raised for unexpected exceptions from the DynamoDB service or unexpected data returned by it"""
    def __init__(self, details: str = None) -> None:
        super().__init__(details or 'Unexpected database error')
