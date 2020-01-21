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
            'required': True,
        },
        'password': {
            'type': 'string',
            'required': True,
        },
        'createdAt': {
            'type': 'float',
            'required': False,
        },
    }
    _validator = Validator(_schema, allow_unknown=False)

    @classmethod
    def validate(cls, newUser):
        return cls._validator.validate(newUser)

class UpdateUser:
    """
    A namespae for update-user related operations
    """
    _schema = {
        'userId': {
            'type': 'string',
            'required': True,
        },
        'password': {
            'type': 'string',
            'required': False,
        },
        'displayName': {
            'type': 'string',
            'required': False,
        },
    }
    _validator = Validator(_schema, allow_unknown=True)

    @classmethod
    def validate(cls, updateUser):
        return cls._validator.validate(updateUser)

    @classmethod
    def getUpdatableFields(cls):
        fields = [
            field for field in cls._schema.keys()
            if cls._schema[field]['required'] == False
        ]
        
        return fields