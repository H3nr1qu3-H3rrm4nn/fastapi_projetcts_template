class ResponseModel:
    def __init__(self, status_code, message, object):
        self.status_code = status_code
        self.message = message
        self.object = object

    def response_model(self):
        return {
            "status_code": self.status_code,
            "message": self.message,
            "object": self.object
        }
