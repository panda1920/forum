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
        elif operator == 'page':
            return PageFilter(querystringObj)

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
    def __init__(self, querystringObj):
        pass

class GTFilter:
    """
    Greather than filter
    """
    def __init__(self, querystringObj):
        pass

class GTEFilter:
    """
    Greather than or equal to filter
    """
    def __init__(self, querystringObj):
        pass

class LTFilter:
    """
    Less than filter
    """
    def __init__(self, querystringObj):
        pass

class LTEFilter:
    """
    Less than or equal to filter
    """
    def __init__(self, querystringObj):
        pass
    
class EQFilter:
    """
    Exact match filter
    """
    def __init__(self, querystringObj):
        pass
    
class RegexFilter:
    """
    Regular expression filter
    """
    def __init__(self, querystringObj):
        pass
    
class PageFilter:
    """
    Deals with pagination
    """
    def __init__(self, querystringObj):
        pass    
    