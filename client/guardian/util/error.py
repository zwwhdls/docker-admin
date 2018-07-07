class BaseError(Exception):

    def __init__(self, error_message):
        self.error_message = error_message

    def render(self):
        return {
            "error_id": self.__class__.__name__,
            "error_message": self.error_message,
        }


class ApiError(Exception):

    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

    def render(self):
        return {
            "error_id": self.error.__class__.__name__,
            "error_message": self.error.error_message,
        }
