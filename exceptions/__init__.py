class KnownException(Exception):
    def __init__(self, code: int = 400, message: str = "Unknown user exception"):
        self.code = code
        self.message = message
        super(KnownException, self).__init__(message)
