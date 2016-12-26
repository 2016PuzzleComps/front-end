import sys
import flask
import json
import hashlib
import time
from validation import *

app = flask.Flask(__name__)

@app.route('/')
def get_index():
    return flask.render_template('present.html')

# receive new solve log file from client
@app.route('/validate', methods=['POST'])
def post_log_file():
    try:
        request = json.loads(flask.request.data.decode('utf-8'))
        puzzle_file = request['puzzle_file']
        log_file = request['log_file']
        # see if the log is a valid solution
        if solve_log_is_valid(puzzle_file, log_file):
            response = {'success': True}
        else:
            response = {'success': False, 'message': "Invalid solve log! What are you up to..."}
    except json.decoder.JSONDecodeError:
        response = {'success': False, 'message': "Invalid JSON! What are you up to..."}
    # send response
    return json.dumps(response)

# verify that a log file represents a valid solve
def solve_log_is_valid(puzzle_file, log_file):
    log_file = log_file.strip()
    if log_file == '':
        return False
    board = Board(puzzle_file)
    vehicle_index = 0
    vector = 0
    prev_timestamp = 0
    try:
        for move in log_file.split('\n'):
            if move == '':
                return False
            move = move.split(' ')
            timestamp = int(move[0])
            if not timestamp > prev_timestamp:
                return False
            prev_timestamp = timestamp
            if len(move) == 2:
                if move[1] == 'R':
                    board = Board(puzzle_file)
                elif move[1] == 'U':
                    board.move_vehicle(vehicle_index, -1 * vector)
                else:
                    return False
            elif len(move) == 3:
                vehicle_index = int(move[1])
                vector = int(move[2])
                if not board.move_vehicle(vehicle_index, vector):
                    return False
            else:
                return False
        #We want any board ending state to be valid, so we just check if
        #each move is valid, not if they solved it
        #return board.is_solved()
        
        return True
    except:
        return False

if __name__ == '__main__':
    host = sys.argv[1]
    port = int(sys.argv[2])
    app.run(host=host, port=port)