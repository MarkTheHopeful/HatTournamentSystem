class LogicException(Exception):
    code = 400

    def __init__(self, code=400, message="Unknown logic error"):
        self.code = code
        self.message = message
        super(LogicException, self).__init__(message)


class LogicGameSizeException(LogicException):
    def __init__(self):
        super(LogicGameSizeException, self).__init__(code=400, message="Game should consist at least of two pairs")
