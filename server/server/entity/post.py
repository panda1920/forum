from cerberus import Validator

class NewPost:
    """
    A namespace for new-post related operations
    """
    _schema = {
        'userId': {
            'type': 'string',
            'required': True,
        },
        'content': {
            'type': 'string',
            'required': True,
        },
        'postId': {
            'type': 'string',
            'required': False,
        },
        'createdAt': {
            'type': 'float',
            'required': False,
        }
    }
    _validator = Validator(_schema, allow_unknown=False)

    @classmethod
    def validate(cls, newPost):
        return cls._validator.validate(newPost)

    @classmethod
    def getFields(cls):
        return cls._schema.keys()

class UpdatePost:
    """
    A namespace for update-post related operations
    """
    _schema = {
        'content': {
            'type': 'string',
            'required': False,
        },
        'postId': {
            'type': 'string',
            'required': True,
        },
    }
    _validator = Validator(_schema, allow_unknown=False)

    @classmethod
    def validate(cls, updatePost):
        return cls._validator.validate(updatePost)

    @classmethod
    def getUpdatableFields(cls):
        fields = [
            field for field in cls._schema.keys()
            if cls._schema[field]['required'] == False
        ]
        
        return fields