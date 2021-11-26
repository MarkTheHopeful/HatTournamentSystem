from sqlalchemy.exc import IntegrityError


class DBException(Exception):
    code = 699

    def __init__(self, code=699, message="Unknown DB error"):
        self.code = code
        self.message = message
        super(DBException, self).__init__(message)


class DBObjectNotFound(DBException):
    def __init__(self, object_name):
        super(DBObjectNotFound, self).__init__(601, f"{object_name} not found")


class DBObjectAlreadyExists(DBException):
    def __init__(self, object_name):
        super(DBObjectAlreadyExists, self).__init__(602, f"{object_name} is already exists")
