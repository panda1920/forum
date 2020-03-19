class MyAppException(Exception):
    """
    Base class for all exceptions of my app
    """
    @classmethod
    def getStatusCode(cls):
        """
        returns corresponding http status code as integer
        """
        raise NotImplementedError

    def getErrorMsg(self):
        """
        returns error message
        """
        return str(self)


# client-side error
class FilterParseError(MyAppException):
    """
    Thrown when parsing failed during construction of filters
    """
    @classmethod
    def getStatusCode(cls):
        return 400


class InvalidFilterOperatorError(MyAppException):
    """
    Thrown when invalid filter operator was given to parse
    """
    @classmethod
    def getStatusCode(cls):
        return 400


class EntityValidationError(MyAppException):
    """
    Raised when validation of entities fails
    """
    @classmethod
    def getStatusCode(cls):
        return 400


class MissingQueryStringError(MyAppException):
    """
    Raised when API was not used properly;
    expected query string was not found in endpoint
    """
    @classmethod
    def getStatusCode(cls):
        return 400


class RequestDataTypeMismatchError(MyAppException):
    """
    Raised when data in request did not contain expected data type
    """
    @classmethod
    def getStatusCode(cls):
        return 400


class InvalidUserCredentials(MyAppException):
    """
    Raised when provided user credential in request was invalid
    """
    @classmethod
    def getStatusCode(cls):
        return 400


class InvalidSession(MyAppException):
    """
    Raised when session information was unexpectedly missing information.
    """
    @classmethod
    def getStatusCode(cls):
        return 400


class InvalidImageFileError(MyAppException):
    """
    Raised when non-valid image file was uploaded
    """
    @classmethod
    def getStatusCode(cls):
        return 400


class IdNotSpecifiedError(MyAppException):
    """
    Raised when Id was not specified for CRUD operations against entity
    """
    @classmethod
    def getStatusCode(cls):
        return 400
        

class RecordNotFoundError(MyAppException):
    """
    Raised when record was not found during db search
    """
    @classmethod
    def getStatusCode(cls):
        return 404


# server-side error
class ServerMiscError(MyAppException):
    """
    A general server-side exception
    """
    @classmethod
    def getStatusCode(cls):
        return 500


class FailedMongoOperation(MyAppException):
    """
    Failed to perform CRUD operation
    """
    @classmethod
    def getStatusCode(cls):
        return 500


class DuplicateUserError(MyAppException):
    """
    User was found when signup
    """
    @classmethod
    def getStatusCode(cls):
        return 500


class FailedAWSOperation(MyAppException):
    """
    Operation on external AWS service failed
    """
    @classmethod
    def getStatusCode(cls):
        return 500


class ValueNotFoundOnContext(MyAppException):
    """
    Failed to find value in flask context proxies like flask.g
    """
    @classmethod
    def getStatusCode(cls):
        return 500
