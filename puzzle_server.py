import sys
import flask
from flask import request, make_response
import psycopg2
import json
import config1 as config
import hashlib
import time
import random
from validation import *

app = flask.Flask(__name__)

### ROUTES ###

@app.route('/')
def get_index():
    resp = make_response(flask.render_template('index.html'))
    print(request.cookies)
    solver_id = request.cookies.get('solver_id')
    if not solver_id or solver_id not in solvers_table:
        solver_id = create_new_solver_id(request)
        resp.set_cookie('solver_id', solver_id)
        solvers_table[solver_id] = Solver()
    # resp.set_cookie('solver_id', '')
    # ^^ for when you want to clear the cookie, for testing purposes
    return resp

@app.route('/tutorial')
def get_tutorial():
    return flask.render_template('tutorial.html')

# serve puzzles to clients
@app.route('/puzzle', methods=['GET'])
def get_puzzle_file():
    solver_id = request.cookies.get('solver_id')
    if not solver_id:
        response = {'success': False, 'message': 'No solver_id set! How on earth...'}
    else:
        puzzle_id = get_appropriate_puzzle_id(solver_id)
        puzzle_file = get_puzzle_file_from_database(puzzle_id)
        response = {'success': True, 'puzzle_id': puzzle_id, 'puzzle_file': puzzle_file}
    return json.dumps(response)

# receive new solve log file from client
@app.route('/log', methods=['GET'])
def post_log_file():
    try:
        request = json.loads(flask.request.data.decode('utf-8'))
        status = request['status']
        # see if the log is valid in light of whether or not they purport to have solved it
        log_file = request['log_file'].strip()
        puzzle_id = request['puzzle_id']
        puzzle_file = get_puzzle_file_from_database(puzzle_id)
        if solve_log_is_valid(puzzle_file, log_file, status):
            solver_id = request.cookies.get('solver_id')
            if not solver_id:
                response = {'success': False, 'message': 'No solver_id set! How on earth...'}
            else:
                update_solvers_table(solver_id, puzzle_id, log_file, status)
                response = {'success': True}
        else:
            response = {'success': False, 'message': "Invalid solve log! What are you up to..."}
    except json.decoder.JSONDecodeError:
        response = {'success': False, 'message': "Invalid JSON! What are you up to..."}
    # send response
    return json.dumps(response)

### DATA ###

# dictionary that stores info about each solver
solvers_table = {}

# object to store info about a solver
class Solver:
    def __init__(self):
        self.num_solves = 0
        self.score = None
    def update(self, newest_score):
        # DO STUFF (I will figure out later)
        pass

### HELPER FUNCTIONS ###

# create a new cookie value to remember the solver by
def create_new_solver_id(request):
    food = str(request.user_agent) + str(time.time())
    m = hashlib.md5()
    m.update(food.encode('UTF-8'))
    return m.hexdigest()

# gets id of a good next puzzle for a solver based on their solver score
def get_appropriate_puzzle_id(solver_id):
    # DO STUFF (I will figure out later)
    return 100

# update the score of a solver after they've solved a puzzle
def update_solvers_table(solver_id, puzzle_id, log_file, status):
    puzzle_score = get_puzzle_score(puzzle_id)
    log_score = get_log_score(log_file)
    # DO STUFF (I will figure out later)

def get_puzzle_score(puzzle_id):
    query = ("SELET min_moves, weighted_walk_length FROM puzzles WHERE puzzle_id = '%s';", (puzzle_id,))
    results = select_from_database(query)
    min_moves, weighted_walk_length = results[0]
    # NEED COEFFICIENTS
    alpha = 1
    beta = 1
    return alpha * min_moves + beta * weighted_walk_length

def get_log_score(log_file):
    moves = log_file.split('\n')
    first_move = moves[0]
    last_move = moves[-1]
    time_taken = (int(last_move.split(' ')[0]) - int(first_move.split(' ')[0]))/1000
    # NEED COEFFICIENTS
    ceta = 1
    deta = 1
    c = 0
    return ceta * len(moves) + deta * time_taken + c

# load puzzle file from db given its ID
def get_puzzle_file_from_database(puzzle_id):
    query = ("SELECT puzzle_file FROM puzzles WHERE puzzle_id = '%s';", (puzzle_id,))
    print("QUERY: " + str(query))
    rows = select_from_database(query)
    print("ROWS: " + str(rows))
    puzzle_file = rows[0][0]
    return puzzle_file

def select_from_database(query):
    cursor.execute(query[0], query[1])
    return cursor.fetchall()

if __name__ == '__main__':
    try:
        connection = psycopg2.connect(user=config.username, password=config.password)
        cursor = connection.cursor()
    except Exception as e:
        print(e)
        exit(1)
    host = sys.argv[1]
    port = int(sys.argv[2])
    app.run(host=host, port=port, threaded = True)
    connection.close()
