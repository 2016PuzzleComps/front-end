import sys
import flask
import psycopg2
import json
import config

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

# get ID of a puzzle with fewest ot tied for fewest logs in DB
def get_next_puzzle_id():
    query = ('SELECT s.puzzle_id as puzzle_id, s.count as num_solves FROM (SELECT puzzle_id, count(solve_id) FROM solve_info GROUP BY puzzle_id) as s WHERE s.count in (SELECT min(t.count) FROM (SELECT count(solve_id) FROM solve_info GROUP BY puzzle_id) as t);', ())
    rows = fetch_all_rows_for_query(query)
    if not rows:
        return None
    return rows[0][0]

# load puzzle file from db given its ID
def get_puzzle_file_from_database(puzzle_id):
    puzzleFile = 'puzzle' + str(puzzle_id) + '.txt'
    return open(puzzleFile).read()

# load a solve log file into the DB
# NOTE: I am assuming the log_file is string with a move per line
def add_log_file_to_database(solve_id, log_file):
    moves = log_file.splitlines;
    move_num = 0
    for move in moves:
        items = move.split()
        timestamp = items[0]
        move = items[1] + items[2]
        query = ('INSERT INTO solve_logs values(%i, %i, %s, %s)', (solve_id, move_num, timestamp, move))
        # NOTE: not sure if the db returns anything on an insert
        rows = fetch_all_rows_for_query(query)
        move_num++

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
        try_print(e)
        exit(1)
    host = sys.argv[1]
    port = sys.argv[2]
    app.run(host=host, port=port)
    connection.close()
