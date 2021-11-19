import app.functions as functions
from app import app


@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"


@app.route('/api/v1/service/status', methods=['GET'])
def status():
    return functions.status()


@app.route('/api/v1/user/login/<username>/<password>', methods=['GET'])
def login(username, password):
    return functions.login(username, password)


@app.route('/api/v1/user/register/<username>/<password>', methods=['GET'])
def register(username, password):
    return functions.register(username, password)


@app.route('/api/v1/admin/drop/<secret_code>', methods=['GET'])
def drop_table(secret_code):
    return functions.drop_tables(secret_code)
