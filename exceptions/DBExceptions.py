from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError


class DBException(Exception):
    code = 500

    def __init__(self, code=500, message="Unknown DB error"):
        self.code = code
        self.message = message
        super(DBException, self).__init__(message)


class DBObjectNotFound(DBException):
    def __init__(self, object_name):
        super(DBObjectNotFound, self).__init__(404, f"{object_name} not found")


class DBObjectAlreadyExists(DBException):
    def __init__(self, object_name):
        super(DBObjectAlreadyExists, self).__init__(400, f"{object_name} is already exists")
