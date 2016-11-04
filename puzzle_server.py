import sys
import flask
import psycopg2
import json
import config1 as config
import hashlib
import time

app = flask.Flask(__name__)

class DatabaseException(Exception):
    pass

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
    m = hashlib.md5()
    food = str(puzzle_id) + '.' + str(time.time())
    m.update(food.encode('utf-8'))
    return m.hexdigest()

# get ID of a puzzle with fewest or tied for fewest logs in DB
def get_next_puzzle_id():
    query = ('SELECT puzzle_id FROM puzzles_by_id WHERE num_solves IN (SELECT min(num_solves) FROM puzzles_by_id )', ())
    rows = select_from_database(query)
    puzzle_id = rows[0][0]
    return puzzle_id

# load puzzle file from db given its ID
def get_puzzle_file_from_database(puzzle_id):
    query = ('SELECT puzzle_file FROM puzzles_by_id WHERE puzzle_id = %s', (puzzle_id,))
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
    # then increment num_solves for the puzzle_id
    query = ('UPDATE puzzles_by_id SET num_solves = (num_solves + 1) WHERE puzzle_id IN (SELECT puzzle_id FROM solve_info WHERE solve_id = %s)', (solve_id,))
    insert_into_database(query)
    # update the solve_info table to record the type of response (completed or gave up)
    query = ('UPDATE solve_info SET status = %s WHERE solve_id = %s', (status, solve_id))
    insert_into_database(query)

class Board:
    class Vehicle:
        def __init__(self, line):
            split = line.split(" ")
            self.x = int(split[0])
            self.y = int(split[1])
            self.size = int(split[2])
            self.is_horiz = split[3] == 'T'
    def __init__(self, puzzle_file):
        lines = puzzle_file.split("\n")
        self.width, self.height = lines[0].split(" ")
        self.vehicles = []
        for i in range(len(lines) - 1):
            self.vehicles.append(Vehicle(lines[i]))
        self.vip = self.vehicles[0]
        self.occupied = set()
        for i in range(self.width):
            self.occupied.add((i,-1))
            self.occupied.add((i,self.height))
        for i in range(self.height):
            self.occupied.add((-1,i))
            self.occupied.add((self.width,i))
        self.occupied.remove((self.width, self.vip.y))
        for v in self.vehicles:
            if v.is_horiz:
                for i in range(v.size):
                    self.occupied.add(v.x + i, v.y)
            else:
                for i in range(v.size):
                    self.occupied.add(v.x, v.y + i)
    
    def move_vehicle(self, vehicle_index, vector):
        v = self.vehicle[vehicle_index]
        for i in range(abs(vector)):
            if not move_vehicle_by_one(v, (vector > 0)):
                return False
        return True

    def move_vehicle_by_one(self, v, forward):
        if v.is_horiz:
            if forward:
                if [(v.x + v.size + 1, v.y)] in self.occupied:
                    return False
                else:
                    self.occupied.remove((v.x, v.y))
                    v.x += 1
                    self.occupied.add((v.x + v.size, v.y))
            else:
                if [(v.x - 1, v.y)] in self.occupied:
                    return False
                else:
                    self.occupied.remove((v.x + v.size, v.y))
                    v.x -= 1
                    self.occupied.add((v.x, v.y))
        else:
            if forward:
                if [(v.x, v.y + v.size + 1)] in self.occupied:
                    return False
                else:
                    self.occupied.remove((v.x, v.y))
                    v.y += 1
                    self.occupied.add((v.x, v.y + v.size))
            else:
                if [(v.x, v.y - 1)] in self.occupied:
                    return False
                else:
                    self.occupied.remove((v.x, v.y + v.size))
                    v.y -= 1
                    self.occupied.add((v.x, v.y))
        return True

    def is_solved(self):
        return self.vip.x + self.vip.size >= self.width

# verify that a log file represents a valid solve
def solve_log_is_valid(solve_id, log_file):
    puzzle_file = get_puzzle_file_from_database(solve_id)
    board = Board(puzzle_file)
    for move in log_file.split("\n"):
        _, vehicle_index, vector = move.split(" ")
        if not board.move_vehicle(vehicle_index, vector):
            return False
    return board.is_solved()

# serve puzzles to clients
@app.route('/puzzle-file', methods=['GET'])
def get_puzzle_file():
    try:
        puzzle_id = get_next_puzzle_id()
        puzzle_file = get_puzzle_file_from_database(puzzle_id)
        solve_id = compute_solve_id(puzzle_id)
        init_new_solve_info(solve_id, puzzle_id)
        response = {'success': True, 'solve_id': solve_id, 'puzzle_file': puzzle_file}
    except DatabaseException:
        response = {'success': False, 'message': "Server error; please reload page and cross fingers!"}
    return json.dumps(response)

# receive new solve log file from client
@app.route('/log-file', methods=['POST'])
def put_log_file():
    request = json.loads(flask.request.data.decode('utf-8'))
    solve_id = request['solve_id']
    status = request['status']
    solve_info = get_solve_info(solve_id)
    if solve_info:
        log_file = request['log_file']
        puzzle_id, mturk_token = solve_info
        if status == 1:
            if not solve_log_is_valid(puzzle_id, log_file):
                response = {'success': False, 'message': "Invalid solve log! What are you up to..."}
                return json.dumps(response)
        try:
            submit_log_file(solve_id, puzzle_id, log_file, status)
            response = {'success': True, 'mturk_token': mturk_token}
            return json.dumps(response)
        except DatabaseException:
            response = {'success': False, 'message': "Server error; please reload page and cross fingers!"}
            return json.dumps(response)
    else:
        response = {'success': False, 'message': "Invalid solve_id! You sly dog..."}
        return json.dumps(response)

def select_from_database(query):
    try:
        print(query)
        cursor.execute(query[0], query[1])
        return cursor.fetchall()
    except Exception as e:
        raise DatabaseException()

def insert_into_database(query):
    try:
        print(query)
        cursor.execute(query[0], query[1])
        connection.commit()
    except Exception as e:
        raise DatabaseException()

if __name__ == '__main__':
    try:
        connection = psycopg2.connect(user=config.username, password=config.password)
        cursor = connection.cursor()
    except Exception as e:
        print(e)
        exit(1)
    host = sys.argv[1]
    port = int(sys.argv[2])
    app.run(host=host, port=port)
    connection.close()
