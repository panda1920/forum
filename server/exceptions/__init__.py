class MyAppException(Exception):
    """
    Base class for all exceptions of my app
    """
    def getStatusCode(self):
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
    def getStatusCode(self):
        return 400

class InvalidFilterOperatorError(MyAppException):
    """
    Thrown when invalid filter operator was given to parse
    """
    def getStatusCode(self):
        return 400

class EntityValidationError(MyAppException):
    """
    Raised when validation of entities fails
    """
    def getStatusCode(self):
        return 400

class MissingQueryStringError(MyAppException):
    """
    Raised when API was not used properly;
    expected query string was not found in endpoint
    """
    def getStatusCode(self):
        return 400

class RequestDataTypeMismatchError(MyAppException):
    """
    Raised when data in request did not contain expected data type
    """
    def getStatusCode(self):
        return 400

class RecordNotFoundError(MyAppException):
    """
    Raised when record was not found during db search
    """
    def getStatusCode(self):
        return 404

# server-side error
class ServerMiscError(MyAppException):
    """
    A general server-side exception 
    """
    def getStatusCode(self):
        return 500