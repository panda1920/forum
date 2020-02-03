from cerberus import Validator

class Paging:
    """
    Class that holds information about pagination
    Pagination consists of 2 elements:
        - offset
            amount of records past the first to start displaying
        - limit
            amount of records to display in 1 page
    """
    DEFAULT_OFFSET = 0
    DEFAULT_LIMIT = 50
    _schema = {
        'offset': {
            'type': 'integer',
            'coerce': int,
            'default': DEFAULT_OFFSET,
            'min': 0
        },
        'limit': {
            'type': 'integer',
            'coerce': int,
            'default': DEFAULT_LIMIT,
            'min': 0
        }
    }

    def __init__(self, keyValues = {}):
        parsed = self.parseKeyValues(keyValues)
        self.offset = parsed['offset']
        self.limit = parsed['limit']

    def parseKeyValues(self, keyValues):
        copy = keyValues.copy()
        v = Validator(schema=self._schema, allow_unknown=True)
        if v.validate(copy):
            return v.document

        parsedKeyValues = v.document
        for attribute in v.errors.keys():
            parsedKeyValues[attribute] = self._schema[attribute]['default']
        return parsedKeyValues

class PagingNoLimit(Paging):
    """
    No limit to how many records shown in 1 page
    """
    def __init__(self, keyValues = {}):
        super().__init__(keyValues)

        self.limit = None