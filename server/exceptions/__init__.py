class FilterParseError(Exception):
    """
    Thrown when parsing failed during construction of filters
    """
class InvalidFilterOperatorError(Exception):
    """
    Thrown when invalid filter operator was given to parse
    """