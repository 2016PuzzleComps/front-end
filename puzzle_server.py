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

# TODO: (reilly)
# write database queries for
# (1) get puzzle with default user metric
# (2) get puzzle with user metric appropriate for them based on the 
#      personal user metric they submitted in their most recent log

# serve puzzles to clients
@app.route('/first-puzzle', methods=['GET'])
def get_puzzle_file():
    puzzle_id = get_next_puzzle_id()
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

try:
    connection = psycopg2.connect(user=config.username, password=config.password)
    cursor = connection.cursor()
except Exception as e:
    print(e)
    exit(1)
