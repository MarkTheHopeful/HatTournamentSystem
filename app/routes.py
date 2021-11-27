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


@app.route('/api/v1/tournament/<tournament_name>/players', methods=['GET'])
def get_players(tournament_name):
    token: str = request.get_json()["token"]
    return functions.get_players(token, tournament_name)


@app.route('/api/v1/tournament/<tournament_name>/players', methods=['DELETE'])
def delete_player(tournament_name):
    token: str = request.get_json()["token"]
    name_first: str = request.get_json()["name_first"]
    name_second: str = request.get_json()["name_second"]
    return functions.delete_player(token, tournament_name, name_first, name_second)


@app.route('/api/v1/tournament/<tournament_name>/words', methods=['POST'])
def new_word(tournament_name):
    token: str = request.get_json()["token"]
    word_text: str = request.get_json()["word_text"]
    word_difficulty: int = int(request.get_json()["word_difficulty"])
    return functions.new_word(token, tournament_name, word_text, word_difficulty)


@app.route('/api/v1/tournament/<tournament_name>/words', methods=['GET'])
def get_words(tournament_name):
    token: str = request.get_json()["token"]
    return functions.get_words(token, tournament_name)


@app.route('/api/v1/tournament/<tournament_name>/words', methods=['DELETE'])
def delete_word(tournament_name):
    token: str = request.get_json()["token"]
    word_text: str = request.get_json()["word_text"]
    return functions.delete_word(token, tournament_name, word_text)


@app.route('/api/v1/tournament/<tournament_name>/rounds', methods=['POST'])
def new_round(tournament_name):
    token: str = request.get_json()["token"]
    round_name: str = request.get_json()["round_name"]
    round_difficulty: int = int(request.get_json()["round_difficulty"])  # TODO: seems redundant
    return functions.new_round(token, tournament_name, round_name, round_difficulty)


@app.route('/api/v1/tournament/<tournament_name>/rounds', methods=['GET'])
def get_rounds(tournament_name):
    token: str = request.get_json()["token"]
    return functions.get_rounds(token, tournament_name)


@app.route('/api/v1/tournament/<tournament_name>/rounds', methods=['DELETE'])
def delete_round(tournament_name):
    token: str = request.get_json()["token"]
    round_name: str = request.get_json()["round_name"]
    return functions.delete_round(token, tournament_name, round_name)


@app.route('/api/v1/tournament/<tournament_name>/rounds/player', methods=['POST'])
def add_player_to_round(tournament_name):
    token: str = request.get_json()["token"]
    round_name: str = request.get_json()["round_name"]
    pair_id: int = int(request.get_json()["player_id"])  # FIXME: Actually, you have no way to get player_id
    return functions.add_player_to_round(token, tournament_name, round_name, pair_id)


@app.route('/api/v1/tournament/<tournament_name>/rounds/player', methods=['GET'])
def get_players_from_round(tournament_name):
    token: str = request.get_json()["token"]
    round_name: str = request.get_json()["round_name"]
    return functions.get_players_in_round(token, tournament_name, round_name)


@app.route('/api/v1/tournament/<tournament_name>/rounds/player', methods=['DELETE'])
def delete_player_from_round(tournament_name):
    token: str = request.get_json()["token"]
    round_name: str = request.get_json()["round_name"]
    pair_id: int = int(request.get_json()["player_id"])  # FIXME: Actually, you have no way to get player_id
    return functions.delete_player_from_round(token, tournament_name, round_name, pair_id)


@app.route('/api/v1/tournament/<tournament_name>/subrounds', methods=['POST'])
def new_subround(tournament_name):
    token: str = request.get_json()["token"]
    round_name: str = request.get_json()["round_name"]
    subround_name: str = request.get_json()["subround_name"]
    return functions.new_subround(token, tournament_name, round_name, subround_name)


@app.route('/api/v1/tournament/<tournament_name>/subrounds', methods=['GET'])
def get_subrounds(tournament_name):
    token: str = request.get_json()["token"]
    round_name: str = request.get_json()["round_name"]
    return functions.get_subrounds(token, tournament_name, round_name)


@app.route('/api/v1/admin/drop', methods=['DELETE'])
def drop_table():
    secret_code: str = request.get_json()["secret_code"]
    return functions.drop_tables(secret_code)
