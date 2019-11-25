from server.exceptions import FilterParseError, InvalidOperatorError

class Filter:
    """
    An object that defines search filter
    Passed to database object when querying for records
    Conceptually a filter consists of the following 3 elements:
        - target field
        - values of the field to look for in list
        - operator used to compare the above field value against records in db
    """
    @staticmethod
    def createFilter(querystringObj):
        """
        Factory method to create a derivative instance of Filter
        """
        Filter.validateQuerystringObj(querystringObj)
        
        operator = querystringObj['operator']
        if operator == 'fuzzy':
            return FuzzyStringFilter(querystringObj)
        elif operator == 'gt':
            return GTFilter(querystringObj)
        elif operator == 'gte':
            return GTEFilter(querystringObj)
        elif operator == 'lt':
            return LTFilter(querystringObj)
        elif operator == 'lte':
            return LTEFilter(querystringObj)
        elif operator == 'eq':
            return EQFilter(querystringObj)
        elif operator == 'regex':
            return RegexFilter(querystringObj)
        else:
            raise InvalidOperatorError(f'Operator {operator} is not defined')

    @staticmethod
    def validateQuerystringObj(querystringObj):
        attributes = ['operator', 'value', 'field']
        for attr in attributes:
            if attr not in querystringObj.keys():
                raise FilterParseError(f'querystringObj is missing attribute {attr}')

    def __init__(self, querystringObj):
        pass

    def parse(self, querystringObj):
        raise NotImplementedError

    def isMatch(self, record):
        raise NotImplementedError

class FuzzyStringFilter(Filter):
    """
    Allows fuzzy searches like searching for post that contains a certain substring
    """

class GTFilter(Filter):
    """
    Greather than filter
    """

class GTEFilter(Filter):
    """
    Greather than or equal to filter
    """

class LTFilter(Filter):
    """
    Less than filter
    """

class LTEFilter(Filter):
    """
    Less than or equal to filter
    """
    
class EQFilter(Filter):
    """
    Exact match filter
    """
    
class RegexFilter(Filter):
    """
    Regular expression filter
    """
