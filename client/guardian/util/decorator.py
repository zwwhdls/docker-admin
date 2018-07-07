from flask import request
from functools import wraps
from jsonschema import validate, ValidationError

from guardian.util.error import BaseError, ApiError


class ArgsError(BaseError):
    pass


def parameter_validator(schema):
    def decorator(func):
        @wraps(func)
        def validator(*args, **kwargs):
            json = request.json
            try:
                validate(json, schema)
            except ValidationError as e:
                raise ApiError(
                    ArgsError("Parameter validate Error: {}".format(e)),
                    status_code=400)
            return func(*args, **kwargs)

        return validator

    return decorator
