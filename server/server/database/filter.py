from cerberus import Validator

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

    @classmethod
    def validateQuerystringObj(cls, querystringObj):
        """
        validate that dictionary contains enough information to form a search filter
        """
        v = Validator(schema=cls._filterSchema, allow_unknown=True)
        isValidated = v.validate(querystringObj)
        if not isValidated:
            raise FilterParseError('Failed construting search filter')

    _filterSchema = {
        'field': {
            'required': True,
            'type': 'string'
        },
        'operator' : {
            'required': True,
            'type': 'string'
        },
        'value': {
            'required': True,
            'type': 'list'
        },
    }

    def __init__(self, querystringObj):
        self._field = querystringObj['field']
        self._values = querystringObj['value']

    def getOpString(self):
        """
        get a string that represents filter operation
        used and overrided by subclass
        """
        raise NotImplementedError

    def getMongoFilter(self):
        """
        forumlates a mongo filter that can be used for searching documents
        """
        raise NotImplementedError

    # def parse(self, querystringObj):
    #     raise NotImplementedError

    def isFieldInRecord(self, record):
        return self._field in record.keys()
    
    def matches(self, record):
        """
        Determines if target record matches the filter
        """
        raise NotImplementedError

    def __eq__(self, other):
        if not isinstance(other, Filter):
            return NotImplemented

        return all([
            self.getOpString() == other.getOpString(),
            self._field == other._field,
            self._values == other._values,
        ])

class FuzzyStringFilter(Filter):
    """
    Allows fuzzy searches like searching for post that contains a certain substring
    """
    def getOpString(self):
        return 'fuzzy'

    def getMongoFilter(self):
        concattedWithPipe = '|'.join(self._values)
        return {
            self._field: { '$regex': f'{concattedWithPipe}', '$options': 'i'} 
        }

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
    def getOpString(self):
        return 'gt'

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
    def getOpString(self):
        return 'gte'

    def matches(self, record):
        if not self.isFieldInRecord(record):
            return False
        
        fieldValue = self._values[0]
        return record[self._field] >= fieldValue

class LTFilter(Filter):
    """
    Less than filter
    """
    def getOpString(self):
        return 'lt'

    def matches(self, record):
        if not self.isFieldInRecord(record):
            return False
        
        fieldValue = self._values[0]
        return record[self._field] < fieldValue

class LTEFilter(Filter):
    """
    Less than or equal to filter
    """
    def getOpString(self):
        return 'lte'

    def matches(self, record):
        if not self.isFieldInRecord(record):
            return False
        
        fieldValue = self._values[0]
        return record[self._field] <= fieldValue
    
class EQFilter(Filter):
    """
    Exact match filter
    """
    def getOpString(self):
        return 'eq'

    def getMongoFilter(self):
        return {
            self._field: { '$in': self._values } 
        }

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
