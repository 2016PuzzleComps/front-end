import sys
import flask
import psycopg2
import json
import config1 as config
import hashlib
import time

app = flask.Flask(__name__)

@app.route('/')
def get_index():
    return flask.render_template('index.html')

# compute the MTurk Token for a solve
def compute_mturk_token(solve_id):
    m = hashlib.md5()
    #food = solve_id + str(time.time())
    food = solve_id
    m.update(food.encode('utf-8'))
    return m.hexdigest()

# compute a unique identifier for a solve
def compute_solve_id(puzzle_id):
    #query = ('SELECT num_solves FROM puzzles_by_id WHERE puzzle_id = %s', (puzzle_id,))
    #rows = fetch_all_rows_for_query(query)
    #num_solves = rows[0]
    m = hashlib.md5()
    food = str(puzzle_id) + '.' + str(time.time())
    m.update(food.encode('utf-8'))
    return m.hexdigest()

# get ID of a puzzle with fewest or tied for fewest logs in DB
def get_next_puzzle_id():
    query = ('SELECT puzzle_id FROM puzzles_by_id WHERE num_solves IN (SELECT min(num_solves) FROM puzzles_by_id )', ())
    rows = fetch_all_rows_for_query(query)
    if not rows:
        return None # TODO: deal with this better
    puzzle_id = rows[0][0]
    return puzzle_id

# load puzzle file from db given its ID
def get_puzzle_file_from_database(puzzle_id):
    query = ('SELECT puzzle_file FROM puzzles_by_id WHERE puzzle_id = %s', (puzzle_id,))
    rows = fetch_all_rows_for_query(query)
    puzzle_file = rows[0][0]
    return puzzle_file

# get the puzzle_id associated with a given solve_id
def get_solve_info(solve_id):
    query = ('SELECT puzzle_id, mturk_token FROM solve_info WHERE solve_id = %s', (solve_id,))
    rows = fetch_all_rows_for_query(query)
    if len(rows) > 0:
        return rows[0]
    else:
        return None

# load a solve log file into the DB
def init_new_solve_info(solve_id, puzzle_id):
    # add an entry to solve_info
    mturk_token = compute_mturk_token(solve_id)
    query = ("INSERT INTO solve_info (solve_id, puzzle_id, mturk_token) VALUES (%s, %s, %s)" , (solve_id, puzzle_id, mturk_token))
    insert_rows_for_query(query)

# see if an mturk_token corresponds to a log file
def verify_mturk_token(mturk_token):
    query = ('SELECT COUNT (*) FROM solve_logs WHERE solve_logs.solve_id = solve_info.solve_id AND solve_info.mturk_token = %s', (mturk_token,))
    rows = fetch_all_rows_for_query(query)
    return rows[0] > 0

# load a solve log file into the DB
def add_log_file_to_database(solve_id, puzzle_id, log_file):
    # then add each move in the log to solve_logs
    log_file = log_file.strip()
    moves = log_file.split('\n')
    for move_num in range(len(moves)):
        line = moves[move_num]
        split = line.split(' ')
        print(split)
        timestamp = split[0]
        move = ' '.join(split[1:])
        query = ('INSERT INTO solve_logs VALUES(%s, %s, %s, %s)', (solve_id, move_num, timestamp, move))
        insert_rows_for_query(query)
    # then increment num_solves for the puzzle_id
    query = ('UPDATE puzzles_by_id SET num_solves = (num_solves + 1) WHERE puzzle_id IN (SELECT puzzle_id FROM solve_info WHERE solve_id = %s)', (solve_id,))
    insert_rows_for_query(query)

# serve puzzles to clients
@app.route('/puzzle-file', methods=['GET'])
def get_puzzle_file():
    puzzle_id = get_next_puzzle_id()
    puzzle_file = get_puzzle_file_from_database(puzzle_id)
    solve_id = compute_solve_id(puzzle_id)
    init_new_solve_info(solve_id, puzzle_id)
    response = {'success': True, 'solve_id': solve_id, 'puzzle_file': puzzle_file}
    return json.dumps(response)

# receive new solve log file from client
@app.route('/log-file', methods=['POST'])
def put_log_file():
    request = json.loads(flask.request.data.decode('utf-8'))
    solve_id = request['solve_id']
    log_file = request['log_file']
    solve_info = get_solve_info(solve_id)
    if solve_info:
        puzzle_id, mturk_token = solve_info
        print(log_file)
        add_log_file_to_database(solve_id, puzzle_id, log_file)
        response = {'success': True, 'mturk_token': mturk_token}
        return json.dumps(response)
    else:
        response = {'success': False, 'message': "invalid solve_id"}
        return json.dumps(response)

# Returns a list of rows obtained from the database by the specified SQL query.
# If the query fails for any reason, an empty list is returned.
def fetch_all_rows_for_query(query):
    rows = []
    try:
        print(query)
        cursor.execute(query[0], query[1])
        rows = cursor.fetchall()
    except Exception as e:
        raise e
    return rows

# Executes an insert query and doesn't look for rows to be returned
def insert_rows_for_query(query):
    try:
        print(query)
        cursor.execute(query[0], query[1])
        connection.commit()
    except Exception as e:
        raise e

if __name__ == '__main__':
    try:
        connection = psycopg2.connect(user=config.username, password=config.password)
        cursor = connection.cursor()
    except Exception as e:
        print(e)
        exit(1)
    host = sys.argv[1]
    port = sys.argv[2]
    app.run(host=host, port=port)
    connection.close()
