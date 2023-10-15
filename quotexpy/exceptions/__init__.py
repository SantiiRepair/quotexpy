class Quotex(BaseException):
    def __init__(self, message):
        self.message = message


class QuotexAuthError(BaseException):
    def __init__(self, message):
        self.message = message


class QuotexParser(BaseException):
    def __init__(self, message):
        self.message = message


class QuotexTimeout(BaseException):
    def __init__(self, message):
        self.message = message
