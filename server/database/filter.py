from server.exceptions import FilterParseError, InvalidFilterOperatorError

class Filter:
    """
    An object that defines search filter
    Passed to database object when querying for records
    Conceptually a filter consists of the following 3 elements:
        - target field
        - value(s) of the field to look for
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
            raise InvalidFilterOperatorError(f'Operator {operator} is not defined')

    @staticmethod
    def validateQuerystringObj(querystringObj):
        """
        validate that dictionary passed has required attributes
        """
        attributes = ['operator', 'value', 'field']
        for attr in attributes:
            if attr not in querystringObj.keys():
                raise FilterParseError(f'querystring is missing attribute {attr}')

    def __init__(self, querystringObj):
        self._field = querystringObj['field']
        self._values = querystringObj['value']

    # def parse(self, querystringObj):
    #     raise NotImplementedError

    def matches(self, record):
        """
        Determines if target record matches the filter
        """
        raise NotImplementedError

    def isFieldInRecord(self, record):
        return self._field in record.keys()

class FuzzyStringFilter(Filter):
    """
    Allows fuzzy searches like searching for post that contains a certain substring
    """
    def matches(self, record):
        if not self.isFieldInRecord(record):
            return False
        
        for fieldValue in self._values:
            if record[self._field].find(fieldValue) != -1:
                return True

        return False

class GTFilter(Filter):
    """
    Greater than filter
    """
    def matches(self, record):
        if not self.isFieldInRecord(record):
            return False
        
        # only use the first value
        # the reasoning is that I felt it makes no sense to OR together 
        # greater than comparison filters
        # same goes with gte, lt, lte
        fieldValue = self._values[0]
        return record[self._field] > fieldValue

class GTEFilter(Filter):
    """
    Greater than or equal to filter
    """
    def matches(self, record):
        if not self.isFieldInRecord(record):
            return False
        
        fieldValue = self._values[0]
        return record[self._field] >= fieldValue

class LTFilter(Filter):
    """
    Less than filter
    """
    def matches(self, record):
        if not self.isFieldInRecord(record):
            return False
        
        fieldValue = self._values[0]
        return record[self._field] < fieldValue

class LTEFilter(Filter):
    """
    Less than or equal to filter
    """
    def matches(self, record):
        if not self.isFieldInRecord(record):
            return False
        
        fieldValue = self._values[0]
        return record[self._field] <= fieldValue
    
class EQFilter(Filter):
    """
    Exact match filter
    """
    def matches(self, record):
        if not self.isFieldInRecord(record):
            return False

        for fieldValue in self._values:
            if record[self._field] == fieldValue:
                return True

        return False
    
class RegexFilter(Filter):
    """
    Regular expression filter
    """
