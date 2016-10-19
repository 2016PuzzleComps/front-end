import sys
import flask
import psycopg2

app = flask.Flask(__name__)

@app.route('/')
def get_index():
    return flask.render_template('index.html')

def get_puzzle_file_from_database(puzzle_id):
    pass #TODO

def add_log_file_to_database(puzzle_id, log_file):
    pass #TODO

# store new log file for given puzzle ID in database
@app.route('/log-file', methods=['PUT'])
def put_log_file():
    puzzle_id = flask.args['id']
    pass #TODO

# get a puzzle to solve, determined by which 
# puzzles have the fewest logs in the database
# (or by puzzle id, if given in URL args)
@app.route('/puzzle-file', methods=['GET'])
def get_puzzle_file():
    # for now just load puzzle1.txt
    return open('puzzle1.txt').read()
    if 'id' in flask.args['id']:
        puzzle_id = flask.args['id']
    else:
        pass #TODO
    return get_puzzle_file_from_database(puzzle_id)

host = sys.argv[1]
port = sys.argv[2]
app.run(host=host, port=port)

