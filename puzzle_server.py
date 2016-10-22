import sys
import flask
import psycopg2
import json

app = flask.Flask(__name__)

@app.route('/')
def get_index():
    return flask.render_template('index.html')

# compute the MTurk Token for a solve
def compute_mturk_token(solve_id):
    return "1337"

# compute a unique identifier for a solve
def compute_solve_id(puzzle_id):
    pass

# get ID of a puzzle with fewest logs in DB
def get_next_puzzle_id():
    return 1 # (for now just load puzzle1.txt)

# load puzzle file from db given its ID
def get_puzzle_file_from_database(puzzle_id):
    if puzzle_id == 1:
        return open('puzzle1.txt').read()

# load a solve log file into the DB
def add_log_file_to_database(solve_id, log_file):
    pass #TODO

# serve puzzles to clients
@app.route('/puzzle-file', methods=['GET'])
def get_puzzle_file():
    puzzle_id = get_next_puzzle_id()
    puzzle_file = get_puzzle_file_from_database(puzzle_id)
    solve_id = compute_solve_id(puzzle_id)
    response = {'solve_id': solve_id, 'puzzle_file': puzzle_file}
    return json.dumps(response)

# receive new solve log file from client
@app.route('/log-file', methods=['POST'])
def put_log_file():
    request = json.loads(flask.request.data.decode('utf-8'))
    solve_id = request['solve_id']
    log_file = request['log_file']
    print(log_file)
    add_log_file_to_database(solve_id, log_file)
    response = {'mturk_token': compute_mturk_token(solve_id)}
    return json.dumps(response)

host = sys.argv[1]
port = sys.argv[2]
app.run(host=host, port=port)

