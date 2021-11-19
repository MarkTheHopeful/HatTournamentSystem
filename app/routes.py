from flask import request
import app.functions as functions
from app import app


@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"


@app.route('/api/v1/service/status', methods=['GET'])
def status():
    return functions.status()


@app.route('/api/v1/user/login', methods=['POST'])
def login():
    username: str = request.get_json()["username"]
    password: str = request.get_json()["password"]
    return functions.login(username, password)


@app.route('/api/v1/user/register', methods=['POST'])
def register():
    username: str = request.get_json()["username"]
    password: str = request.get_json()["password"]
    return functions.register(username, password)


@app.route('/api/v1/admin/drop', methods=['DELETE'])
def drop_table():
    secret_code: str = request.get_json()["secret_code"]
    return functions.drop_tables(secret_code)
