import sys
import flask
import psycopg2
import json
import config
import hashlib

app = flask.Flask(__name__)

@app.route('/')
def get_index():
    return flask.render_template('index.html')

# compute the MTurk Token for a solve
def compute_mturk_token(solve_id):
    m = hashlib.md5()
    m.update(solve_id.encode('utf-8'))
    return m.hexdigest().decode('utf-8')

# compute a unique identifier for a solve
def compute_solve_id(puzzle_id):
    query = ('SELECT num_solves FROM puzzles_by_id WHERE puzzle_id = %i', (puzzle_id))
    rows = fetch_all_rows_for_query(query)
    num_solves = rows[0][0]
    m = hashlib.md5()
    to_hash = str(puzzle_id) + '.' + str(num_solves)
    m.update(to_hash.encode('utf-8'))
    return m.hexdigest().decode('utf-8')

# get ID of a puzzle with fewest or tied for fewest logs in DB
def get_next_puzzle_id():
    query = ('select puzzle_id from puzzles_by_id where num_solves in (select min(num_solves) from puzzles_by_id )', ())
    rows = fetch_all_rows_for_query(query)
    if not rows:
        return None # TODO: deal with this better
    puzzle_id = rows[0][0]
    return puzzle_id

# load puzzle file from db given its ID
def get_puzzle_file_from_database(puzzle_id):
    query = ('SELECT puzzle_file FROM puzzles_by_id WHERE puzzle_id = %i;', (puzzle_id))
    rows = fetch_all_rows_for_query(query)
    puzzle_file = rows[0][1]
    return puzzle_file

# load a solve log file into the DB
def add_log_file_to_database(solve_id, log_file):
    moves = log_file.split('\n')
    for move_num in range(len(moves)):
        line = moves[move_num]
        split = line.split(' ')
        timestamp = split[0]
        move = ' '.join(split[1:])
        query = ('INSERT INTO solve_logs values(%i, %i, %s, %s)', (solve_id, move_num, timestamp, move))
        fetch_all_rows_for_query(query)

    # increments num_solve for the puzzle_id
    query = ('update puzzles_by_id set num_solves = (num_solves + 1) where puzzle_id in (select puzzle_id from solve_info where solve_id = %i)', (solve_id))
    fetch_all_rows_for_query(query)

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


# Returns a list of rows obtained from the database by the specified SQL query.
# If the query fails for any reason, an empty list is returned.
def fetch_all_rows_for_query(query):
    rows = []
    try:
        cursor.execute(query[0], query[1])
        rows = cursor.fetchall()
    except Exception as e:
        raise e
    return rows


if __name__ == '__main__':
    try:
        connection = psycopg2.connect(database=config.database, user=config.user, password=config.password)
        cursor = connection.cursor()
    except Exception as e:
        print(e)
        exit(1)
    host = sys.argv[1]
    port = sys.argv[2]
    app.run(host=host, port=port)
    connection.close()
