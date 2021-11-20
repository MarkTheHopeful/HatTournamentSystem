from sqlalchemy.exc import IntegrityError


class DBException(Exception):
    code = 699

    def __init__(self, code=699, message="Unknown DB error"):
        self.code = code
        self.message = message
        super(DBException, self).__init__(message)


class DBUserNotFoundException(DBException):
    def __init__(self, message="No such user in DB"):
        super(DBUserNotFoundException, self).__init__(601, message)


class DBUserAlreadyExistsException(DBException):
    def __init__(self, message="The user is already in DB"):
        super(DBUserAlreadyExistsException, self).__init__(602, message)


class DBTokenNotFoundException(DBException):
    def __init__(self, message="No such token in DB"):
        super(DBTokenNotFoundException, self).__init__(603, message)


class DBPlayerAlreadyExistsException(DBException):
    def __init__(self, message="One of the players is already in DB"):
        super(DBPlayerAlreadyExistsException, self).__init__(604, message)


class DBTournamentNotOwnedException(DBException):
    def __init__(self, message="Tournament does not exists or owned by different user"):
        super(DBTournamentNotOwnedException, self).__init__(605, message)


class DBPairNotFoundException(DBException):
    def __init__(self, message="No such pair in tournament"):
        super(DBPairNotFoundException, self).__init__(606, message)


class DBWordAlreadyExistsException(DBException):
    def __init__(self, message="Word is already in DB"):
        super(DBWordAlreadyExistsException, self).__init__(607, message)


class DBWordNotFoundException(DBException):
    def __init__(self, message="No such word in tournament"):
        super(DBWordNotFoundException, self).__init__(608, message)
