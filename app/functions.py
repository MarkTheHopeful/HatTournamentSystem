# There the functions are being implemented.
# Then the routes.py will use them
# The functions always produce output as JSON
# The format is: {code: CODE, state: STATE, data: {JSON}}, where code is the status code
# State is the description of the code
# And the data is the product, which the function returns


import json
import datetime
from app.extensions import dbm
from utils.encrypt import encrypt_password, check_password
from config import Config
from exceptions.DBExceptions import DBException, DBUserAlreadyExistsException, DBUserNotFoundException, \
    DBTokenNotFoundException
from utils.utils import gen_token, full_stack
from entities.user import User
from entities.tournament import Tournament


class Response:
    code = 500
    data = None

    def __init__(self, code=500, data=None):
        self.code = code
        if data is None:
            data = json.dumps({})
        self.data = json.loads(data)

    def __str__(self):
        return str(json.dumps({"data": self.data}))


def function_response(result_function):
    """
    :param result_function: function to wrap, have to return code (Int) and data (JSON)
    :return: wrapped function, input stays same, exceptions handled, output converted to str(Response)
    Wrapper for all functions in routes
    Gets code and data from the wrapped function and returns a [[app.functions.Response]] object, casted to string
    If an exception occurs, its string goes to the data["Error"] and logs (to stdout)
    Catches DBExceptions with error codes 6xx (699 for unknown db error)
    Catches all other exceptions with error code 500
    """

    def wrapped(*args, **kwargs):
        code = 500
        try:
            code, data = result_function(*args, **kwargs)
        except DBException as e:
            code = e.code
            data = json.dumps({"error": str(e), "stack": full_stack()})
            print("DBException:", e)
        # except GameException as e:
        #     code = 410
        #     data = json.dumps({"Error": str(e), "Stack": full_stack()})
        #     print("GameException:", e)
        except Exception as e:
            data = json.dumps({"error": str(e), "stack": full_stack()})
            print(e)
        return str(Response(code, data)), code

    return wrapped


def token_auth(token):
    """
    :param token: user token, string
    :return: -1, if no such token exists or if the token is outdated, username otherwise
    """
    try:
        username, exp_time = dbm.get_username_and_exptime_by_token(token)
    except DBTokenNotFoundException:
        return -1
    if exp_time < datetime.datetime.utcnow():
        dbm.delete_token(token)
        return -1
    return username


@function_response
def status():  # TODO: rewrite to add meaningful information
    """
    Get the server's state
    :return: 200, 'State' : 'Ok/Failed', 'API version', 'DB manager' : 'Ok/FAILED', 'Game manager': 'Ok/FAILED',
     'Amount of games', 'Length of queue';
    """
    code = 200
    result = {'State': 'Active', 'API version': 'v1', 'DB manager': 'Ok' if dbm.is_ok() else "FAILED"}
    data = json.dumps(result)
    return code, data


@function_response
def login(username, password):
    """
    :param username: not empty, should be real username
    :param password: not empty, should be user's password
    :return: 404, {} if there is no user with such credentials; 200, {'Token': <token>} if there is
    Can throw DBException, but shouldn't
    """
    try:
        u_hash = dbm.get_passhash_by_username(username)
    except DBUserNotFoundException:
        code = 404
        data = json.dumps({})
        return code, data

    if not check_password(password, u_hash):
        code = 404
        data = json.dumps({})
        return code, data

    tok_uuid, tok_exp = gen_token()
    dbm.insert_token_to_username(tok_uuid, tok_exp, username)
    code = 200
    data = json.dumps({'Token': tok_uuid})
    return code, data


@function_response
def register(username, password):
    """
    :param username: new username, should be unique and consist only of allowed characters
    :param password: password, should be strong
    :return: 200, {} if success; 400, {} if username is already in use
    Can throw DBException, but shouldn't
    TODO: add password check
    TODO: add allowed characters list and verification
    """
    pass_hash = encrypt_password(password)
    try:
        dbm.insert_user(User(username=username), pass_hash)
    except DBUserAlreadyExistsException:
        code = 400
        data = json.dumps({})
        return code, data
    finally:
        code = 200
        data = json.dumps({})
    return code, data


@function_response
def new_tournament(token, tournament_name):
    """
    :param token: session token
    :param tournament_name: name of new tournament to create
    :return: 200, {} if success; 403, {} if token is invalid
    """
    username = token_auth(token)
    if username == -1:
        code = 403
        data = json.dumps({})
        return code, data
    dbm.insert_tournament(Tournament(name=tournament_name), username)
    return 200, json.dumps({})


@function_response
def get_tournaments(token):
    """
    :param token: session token
    :return: 200, {"tournaments": <list of tournaments>} if success; 403, {} if token is invalid
    """
    username = token_auth(token)
    if username == -1:
        code = 403
        data = json.dumps({})
        return code, data
    tournaments = dbm.get_tournaments(username)
    return 200, json.dumps({"tournaments": tournaments})


@function_response
def new_player(token, tournament_new, name_first, name_second):
    """
    :param token: session token
    :param tournament_new: name of the tournament to which the players will be added
    :param name_first: name of the first player in pair
    :param name_second: name of the second player in pair
    :return:
    """
    username = token_auth(token)
    if username == -1:
        code = 403
        data = json.dumps({})
        return code, data


@function_response
def drop_tables(secret_code):
    """
    :param secret_code: admin secret from config
    :return: 403, {} if the secret code is incorrect
    200, {} if everything is dropped and recreated successfully
    """
    if secret_code != Config.ADMIN_SECRET:
        return 403, json.dumps({})
    dbm.clear_all_tables()
    return 200, json.dumps({})
