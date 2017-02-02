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

# load puzzle file from db given its ID
def get_puzzle_file_from_database(puzzle_id):
    query = ('SELECT puzzle_file FROM user_metric_data WHERE puzzle_id = %s', (puzzle_id,))
    rows = select_from_database(query)
    puzzle_file = rows[0][0]
    return puzzle_file

# TODO: (reilly)
# write database queries for
# (1) get puzzle with default user metric
# (2) get puzzle with user metric appropriate for them based on the 
#      personal user metric they submitted in their most recent log

# serve puzzles to clients
@app.route('/first-puzzle', methods=['GET'])
def get_puzzle_file():
    puzzle_id = 8  # this is the puzzle with the median user metric
    puzzle_file = get_puzzle_file_from_database(puzzle_id)
    response = {'success': True, 'puzzle_file': puzzle_file}
    return json.dumps(response)

# receive new solve log file from client
@app.route('/next-puzzle', methods=['POST'])
def post_log_file():
    try:
        request = json.loads(flask.request.data.decode('utf-8'))
        status = request['status']
        # see if the log is valid in light of whether or not they purport to have solved it
        log_file = request['log_file'].strip()
        puzzle_solved = request['puzzle_file'].strip()
        if solve_log_is_valid(puzzle_solved, log_file, status):
            puzzle_file = get_next_puzzle(puzzle_solved, log_file, status)
            response = {'success': True, 'puzzle_file': puzzle_file}
        else:
            response = {'success': False, 'message': "Invalid solve log! What are you up to..."}
    except json.decoder.JSONDecodeError:
        response = {'success': False, 'message': "Invalid JSON! What are you up to..."}
    # send response
    return json.dumps(response)

def get_next_puzzle(puzzle_solved, log_file, status):
    # TODO: take into account whether or not they gave up
    moves = log_file.split('\n')
    num_moves = len(moves)
    first_move = moves[0]
    last_move = moves[len(moves)-1]
    time_taken = (int(last_move.split(' ')[0]) - int(first_move.split(' ')[0]))/1000
    print("Time Taken:", time_taken)
    print("Num Moves:", num_moves)
    #print(puzzle_solved)
    query = ('SELECT weighted_walk_length, min_moves FROM user_metric_data WHERE puzzle_file = %s', (puzzle_solved,))
    #print(query)
    results = select_from_database(query)
    #print(results[0])
    weighted_walk_length = results[0][0]
    min_moves = results[0][1]

    user_metric = (float(time_taken)*float(num_moves)*float(weighted_walk_length))/float(min_moves)

    user_metric_min = 6632.06807757353
    user_metric_max = 569475.962297654

    scaled_user_metric = (user_metric - user_metric_min) / (user_metric_max - user_metric_min)
    if (scaled_user_metric < 0):
        scaled_user_metric = 0
        new_puzzle_metric = 100
    elif (scaled_user_metric > 100):
        scaled_user_metric = 100
        new_puzzle_metric = 0
    else:
        if (scaled_user_metric > 25):
            difference = scaled_user_metric - 25
            new_puzzle_metric = 25 - difference
        else:
            difference = 25 - scaled_user_metric
            new_puzzle_metric = 25 + difference

    print("User Metric:", user_metric)
    print("User Metric Scaled:", scaled_user_metric)
    print("New Puzzle Metric:", new_puzzle_metric)



    query = ('SELECT puzzle_file FROM user_metric_data ORDER BY ABS(user_metric_scaled - %s)', (new_puzzle_metric,))
    results = select_from_database(query)
    puzzle_file = results[0][0]
    return puzzle_file

def select_from_database(query):
    print(query)
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
