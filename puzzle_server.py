import sys
import flask
from flask import request, make_response
import psycopg2
import json
import config1 as config
import hashlib
import time
import random
import math
from validation import *

app = flask.Flask(__name__)

@app.route('/')
def get_index():
    resp = make_response(flask.render_template('index.html'))
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
        response = {'success': False, 'message': 'No solver_id set!'}
    else:
        puzzle_id = get_appropriate_puzzle_id(solver_id)
        puzzle_file = get_puzzle_file_from_database(puzzle_id)
        response = {'success': True, 'puzzle_id': puzzle_id, 'puzzle_file': puzzle_file, 'stats': {'puzzle_score': get_puzzle_score(puzzle_id)}}
    return json.dumps(response)

# receive new solve log file from client
@app.route('/log', methods=['POST'])
def post_log_file():
    try:
        request_json = json.loads(flask.request.data.decode('utf-8'))
        status = request_json['status']
        log_file = request_json['log_file'].strip()
        puzzle_id = request_json['puzzle_id']
        puzzle_file = get_puzzle_file_from_database(puzzle_id)
        # see if the log is valid in light of whether or not they purport to have solved it
        if solve_log_is_valid(puzzle_file, log_file, status):
            solver_id = request.cookies.get('solver_id')
            if not solver_id:
                response = {'success': False, 'message': 'No solver_id set!'}
            else:
                stats = update_solvers_table(solver_id, puzzle_id, log_file, status)
                response = {'success': True, 'stats': {'log_score': get_log_score(log_file), 'solver_score': solvers_table[solver_id].get_solver_score()}}
        else:
            response = {'success': False, 'message': "Invalid solve log! What are you up to..."}
    except json.decoder.JSONDecodeError as e:
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
        self.ratio = 1
        self.completedPuzzles = []
    def update(self, puzzle_score, log_score):
        # weighted average of sqrt'ed ratios, weighting newer ones higher
        new_ratio = math.sqrt(puzzle_score/log_score)
        self.ratio = (self.ratio*self.num_solves + new_ratio)/(self.num_solves + 1)
        self.num_solves += 1
    def get_solver_score(self):
        return self.ratio
    def add_completed_puzzle(self, puzzle_id):
        self.completedPuzzles.append(puzzle_id)

### HELPER FUNCTIONS ###

# create a new cookie value to remember the solver by
def create_new_solver_id(request):
    food = str(request.user_agent) + str(time.time())
    m = hashlib.md5()
    m.update(food.encode('UTF-8'))
    return m.hexdigest()

# update the score of a solver after they've solved a puzzle
def update_solvers_table(solver_id, puzzle_id, log_file, status):
    solver = solvers_table[solver_id]
    puzzle_score = get_puzzle_score(puzzle_id)
    log_score = get_log_score(log_file)
    print("puzzle id: " + str(puzzle_id))
    print("puzzle score: " + str(puzzle_score))
    print("log score: " + str(log_score))
    solver.update(puzzle_score, log_score)
    solver.add_completed_puzzle(puzzle_id)

# gets id of a good next puzzle for a solver based on their solver score
def get_appropriate_puzzle_id(solver_id):
    solver = solvers_table[solver_id]
    ideal_score = 500 # TODO: figure out what we want the 'ideal' puzzle/log score to be
    if solver.num_solves == 0:
        target_puzzle_score = ideal_score
    else:
        target_puzzle_score = ideal_score * solver.get_solver_score()
    target_puzzle_score = 500
    query = ("SELECT puzzle_id FROM puzzles ORDER BY ABS(((7.52*weighted_walk_length) - (0.014*(weighted_walk_length^2)) + 171.24) - %s) LIMIT 100;", (target_puzzle_score,))
    rows = select_from_database(query)
    #makes sure user doesn't receive already solved puzzle
    i=0
    while rows[i][0] in solver.completedPuzzles:
        i = i+1
    print (rows[i][0])
    return rows[i][0]

def get_puzzle_score(puzzle_id):
    query = ("SELECT weighted_walk_length FROM puzzles WHERE puzzle_id = '%s';", (puzzle_id,))
    rows = select_from_database(query)
    weighted_walk_length = int(rows[0][0])
    alpha = 7.25
    beta = -0.014
    c = 171.24
    return (alpha * weighted_walk_length) + (beta * weighted_walk_length * weighted_walk_length) + c

def get_log_score(log_file):
    moves = log_file.split('\n')
    num_moves = len(moves)
    first_move = moves[0]
    last_move = moves[-1]
    time_taken = (int(last_move.split(' ')[0]) - int(first_move.split(' ')[0]))/1000
    ceta = .5
    deta = 6
    return (ceta * time_taken) + (deta * num_moves)

# load puzzle file from db given its ID
def get_puzzle_file_from_database(puzzle_id):
    query = ("SELECT puzzle_file FROM puzzles WHERE puzzle_id = '%s';", (puzzle_id,))
    rows = select_from_database(query)
    puzzle_file = rows[0][0]
    return puzzle_file

def select_from_database(query):
    try:
        # print("QUERY: " + str(query))
        connection = psycopg2.connect(user=config.username, password=config.password)
        cursor = connection.cursor()
        cursor.execute(query[0], query[1])
        rows = cursor.fetchall()
        # print("ROWS: " + str(rows))
        connection.close()
        return rows
    except Exception as e:
        print(e)
        exit(1)

if __name__ == '__main__':
    host = sys.argv[1]
    port = int(sys.argv[2])
    app.run(host=host, port=port, threaded = True)
