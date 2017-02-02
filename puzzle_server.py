import sys
import flask
import psycopg2
import json
import config1 as config
import hashlib
import time
import random
from validation import *

app = flask.Flask(__name__)

@app.route('/')
def get_index():
    return flask.render_template('index.html')

@app.route('/tutorial')
def get_tutorial():
    return flask.render_template('tutorial.html')

# compute the MTurk Token for a solve
def compute_mturk_token(solve_id):
    m = hashlib.md5()
    food = solve_id + str(time.time())
    m.update(food.encode('utf-8'))
    return m.hexdigest()

# compute a unique identifier for a solve
def compute_solve_id(puzzle_id):
    m = hashlib.md5()
    food = str(puzzle_id) + '.' + str(time.time())
    m.update(food.encode('utf-8'))
    return m.hexdigest()

# get ID of a puzzle with fewest or tied for fewest logs in DB
def get_next_puzzle_id():
    #query = ('SELECT COUNT (*) FROM puzzles_by_id', ())
    #rows = select_from_database(query)
    #num_puzzles = rows[0][0]
    #puzzle_id = random.randint(0, num_puzzles-1)
    #return puzzle_id
    
    query = ('SELECT puzzle_id FROM puzzles_by_id WHERE num_solves IN (SELECT min(num_solves) FROM puzzles_by_id )', ())
    rows = select_from_database(query)
    puzzle_id = rows[0][0]
    return puzzle_id



# load puzzle file from db given its ID
def get_puzzle_file_from_database(puzzle_id):
    query = ('SELECT puzzle_file FROM user_metric_data WHERE puzzle_id = %s', (puzzle_id,))
    rows = select_from_database(query)
    puzzle_file = rows[0][0]
    return puzzle_file

# get the puzzle_id associated with a given solve_id
def get_solve_info(solve_id):
    query = ('SELECT puzzle_id, mturk_token FROM solve_info WHERE solve_id = %s', (solve_id,))
    rows = select_from_database(query)
    if len(rows) > 0:
        return rows[0]
    else:
        return None

# load a solve log file into the DB
def init_new_solve_info(solve_id, puzzle_id):
    # add an entry to solve_info
    mturk_token = compute_mturk_token(solve_id)
    #status is 0 - awaiting response
    status = "0"
    query = ("INSERT INTO solve_info (solve_id, puzzle_id, mturk_token, status) VALUES (%s, %s, %s, %s)" , (solve_id, puzzle_id, mturk_token, status))
    insert_into_database(query)

# see if an mturk_token corresponds to a log file
def verify_mturk_token(mturk_token):
    query = ('SELECT COUNT (*) FROM solve_logs WHERE solve_logs.solve_id = solve_info.solve_id AND solve_info.mturk_token = %s', (mturk_token,))
    rows = select_from_database(query)
    return rows[0] > 0

# load a solve lo  file into the DB
def submit_log_file(solve_id, puzzle_id, log_file, status):
    # add each move in the log to solve_logs
    log_file = log_file.strip()
    moves = log_file.split('\n')
    for move_num in range(len(moves)):
        line = moves[move_num]
        split = line.split(' ')
        timestamp = split[0]
        move = ' '.join(split[1:])
        query = ('INSERT INTO solve_logs VALUES(%s, %s, %s, %s)', (solve_id, move_num, timestamp, move))
        insert_into_database(query)
    # update the solve_info table to record the type of response (completed or gave up)
    query = ('UPDATE solve_info SET status = %s WHERE solve_id = %s', (status, solve_id))
    insert_into_database(query)
    # if they solved it, increment num_solves for the puzzle_id
    if status == 1:
        query = ('UPDATE puzzles_by_id SET num_solves = (num_solves + 1) WHERE puzzle_id IN (SELECT puzzle_id FROM solve_info WHERE solve_id = %s)', (solve_id,))
        insert_into_database(query)

# TODO: (reilly)
# write database queries for
# (1) get puzzle with default user metric
# (2) get puzzle with user metric appropriate for them based on the 
#      personal user metric they submitted in their most recent log

# serve puzzles to clients
@app.route('/puzzle-file', methods=['GET'])
def get_puzzle_file():
    puzzle_id = 100  # this is the puzzle with the median user metric
    puzzle_file = get_puzzle_file_from_database(puzzle_id)
    response = {'success': True, 'puzzle_file': puzzle_file}
    return json.dumps(response)

# receive new solve log file from client
@app.route('/log-file', methods=['POST'])
def post_log_file():
    try:
        request = json.loads(flask.request.data.decode('utf-8'))
        solve_id = request['solve_id']
        status = request['status']
        solve_info = get_solve_info(solve_id)
        # see if they send a valid solve_id
        if solve_info:
            # see if the log is valid in light of whether or not they purport to have solved it
            log_file = request['log_file'].strip()
            puzzle_id, mturk_token = solve_info
            puzzle_file = get_puzzle_file_from_database(puzzle_id).strip()
            if solve_log_is_valid(puzzle_file, log_file, status):
                if status == 1:
                    response = {'success': True}
                else:
                    response = {'success': True}
                # put log file in database
                submit_log_file(solve_id, puzzle_id, log_file, status)
            else:
                response = {'success': False, 'message': "Invalid solve log! What are you up to..."}
        else:
            response = {'success': False, 'message': "Invalid solve_id! You sly dog..."}
    except json.decoder.JSONDecodeError:
        response = {'success': False, 'message': "Invalid JSON! What are you up to..."}
    # send response
    return json.dumps(response)

def select_from_database(query):
    print(query)
    cursor.execute(query[0], query[1])
    return cursor.fetchall()

def insert_into_database(query):
    print(query)
    cursor.execute(query[0], query[1])
    connection.commit()

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
