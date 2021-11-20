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


@app.route('/api/v1/tournament/new', methods=['POST'])
def new_tournament():
    token: str = request.get_json()["token"]
    tournament_name: str = request.get_json()["name"]
    return functions.new_tournament(token, tournament_name)


@app.route('/api/v1/tournament', methods=['GET'])
def get_tournaments():
    token: str = request.get_json()["token"]
    return functions.get_tournaments(token)


@app.route('/api/v1/tournament/<tournament_name>/players', methods=['POST'])
def new_player(tournament_name):
    token: str = request.get_json()["token"]
    name_first: str = request.get_json()["name_first"]
    name_second: str = request.get_json()["name_second"]
    return functions.new_player(token, tournament_name, name_first, name_second)


@app.route('/api/v1/tournament/<tournament_name>/players', methods=['DELETE'])
def delete_player(tournament_name):
    token: str = request.get_json()["token"]
    name_first: str = request.get_json()["name_first"]
    name_second: str = request.get_json()["name_second"]
    return functions.delete_player(token, tournament_name, name_first, name_second)


@app.route('/api/v1/admin/drop', methods=['DELETE'])
def drop_table():
    secret_code: str = request.get_json()["secret_code"]
    return functions.drop_tables(secret_code)
