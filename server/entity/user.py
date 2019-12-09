from cerberus import Validator

class NewUser:
    """
    A namespace for new-user related operations
    """
    _schema = {
        'userId': {
            'type': 'string',
            'required': False,
        },
        'userName': {
            'type': 'string',
            'required': True,
            'regex': r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        },
        'displayName': {
            'type': 'string',
            'required': False,
        },
        'password': {
            'type': 'string',
            'required': True,
        },
        'createdAt': {
            'type': 'float',
            'required': True,
        },
    }
    _validator = Validator(_schema, allow_unknown=False)

    @classmethod
    def validate(cls, newPost):
        return cls._validator.validate(newPost)