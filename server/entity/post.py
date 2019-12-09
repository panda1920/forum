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
            'required': True,
        }
    }
    _validator = Validator(_schema, allow_unknown=False)

    @classmethod
    def validate(cls, newPost):
        return cls._validator.validate(newPost)