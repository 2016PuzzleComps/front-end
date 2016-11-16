from collections import deque

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
        self.width, self.height = map(int, lines[0].split(" "))
        self.vehicles = []
        for i in range(1, len(lines)):
            line = lines[i]
            if line:
                self.vehicles.append(self.Vehicle(line))
            else:
                break
        self.vip = self.vehicles[0]
        self.occupied = set()
        for i in range(self.width):
            self.occupied.add((i,-1))
            self.occupied.add((i,self.height))
        for i in range(self.height):
            self.occupied.add((-1,i))
            self.occupied.add((self.width,i))
        self.occupied.remove((self.width, self.vip.y))
        for i in range(len(self.vehicles)):
            v = self.vehicles[i]
            if v.is_horiz:
                for j in range(v.size):
                    self.occupied.add((v.x + j, v.y))
            else:
                for j in range(v.size):
                    self.occupied.add((v.x, v.y + j))
    
    def move_vehicle(self, move):
        v = self.vehicles[move.vehicle_index]
        if v.is_horiz:
            h = 'T'
        else:
            h = 'F'
        for i in range(abs(move.vector)):
            if not self.move_vehicle_by_one(move.vehicle_index, (move.vector > 0)):
                return False
        return True

    def move_vehicle_by_one(self, vehicle_index, forward):
        v = self.vehicles[vehicle_index]
        if v.is_horiz:
            if forward:
                if (v.x + v.size, v.y) in self.occupied:
                    return False
                else:
                    self.occupied.remove((v.x, v.y))
                    self.occupied.add((v.x + v.size, v.y))
                    v.x += 1
            else:
                if (v.x - 1, v.y) in self.occupied:
                    return False
                else:
                    self.occupied.remove((v.x + v.size - 1, v.y))
                    self.occupied.add((v.x - 1, v.y))
                    v.x -= 1
        else:
            if forward:
                if (v.x, v.y + v.size) in self.occupied:
                    return False
                else:
                    self.occupied.remove((v.x, v.y))
                    self.occupied.add((v.x, v.y + v.size))
                    v.y += 1
            else:
                if (v.x, v.y - 1) in self.occupied:
                    return False
                else:
                    self.occupied.remove((v.x, v.y + v.size - 1))
                    self.occupied.add((v.x, v.y - 1))
                    v.y -= 1
        return True
    
    def show(self):
        print(' 012345')
        for y in range(self.height):
            print(y, end='')
            for x in range(self.width):
                if (x,y) in self.occupied:
                    print('X', end='')
                else:
                    print(' ', end='')
            print('')

    def is_solved(self):
        return self.vip.x + self.vip.size >= self.width

class Move:
    def __init__(self, vehicle_index, vector):
        self.vehicle_index = vehicle_index
        self.vector = vector
    def inverse(self):
        return Move(self.vehicle_index, -1 * self.vector)

# verify that a log file represents a valid solve
def solve_log_is_valid(puzzle_file, log_file, status):
    board = Board(puzzle_file)
    moves_stack = deque()
    vector = 0
    prev_timestamp = 0
    for move_str in log_file.split('\n'):
        if move_str == '':
            return False
        move_str_split = move_str.split(' ')
        timestamp = int(move_str_split[0])
        if not timestamp > prev_timestamp:
            print("here")
            return False
        prev_timestamp = timestamp
        if len(move_str_split) == 2:
            if move_str_split[1] == 'R':
                board = Board(puzzle_file)
                moves_stack.clear()
            elif move_str_split[1] == 'U':
                if len(moves_stack) == 0:
                    return False
                board.move_vehicle(moves_stack[-1].inverse())
                moves_stack.pop()
            else:
                return False
        elif len(move_str_split) == 3:
            move = Move(int(move_str_split[1]), int(move_str_split[2]))
            if not board.move_vehicle(move):
                return False
            moves_stack.append(move)
        else:
            return False
    if status == 1:
        return board.is_solved()
    else:
        return True

if __name__ == '__main__':
    puzzle_file = open('puzzle.txt').read().strip()
    log_file = open('log.txt').read().strip()
    print(solve_log_is_valid(puzzle_file, log_file, 1))
