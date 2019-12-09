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
    DEFAULT_LIMIT = 100
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

    def __init__(self, querystringObj = {}):
        parsed = self.parseQuerystring(querystringObj)
        self.offset = parsed['offset']
        self.limit = parsed['limit']

    def parseQuerystring(self, querystringObj):
        copy = querystringObj.copy()
        v = Validator(schema=self._schema, allow_unknown=True)
        if v.validate(copy):
            return v.document

        parsedQuerystring = v.document
        for attribute in v.errors.keys():
            parsedQuerystring[attribute] = self._schema[attribute]['default']
        return parsedQuerystring

class PagingNoLimit(Paging):
    """
    No limit to how many records shown in 1 page
    """
    def __init__(self, querystringObj = {}):
        super().__init__(querystringObj)

        self.limit = None