from typing import Any

class ResponseModel:
    success: bool
    message: str
    object: Any

    def __init__(self, success: bool, message: str, object: Any):
        self.success = success
        self.message = message
        self.object = object

    def model_response(self):
        return {
            'success': self.success,
            'message': self.message,
            'object': self.object
        }