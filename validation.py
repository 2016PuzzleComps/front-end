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
        for i in range(len(lines) - 2):
            self.vehicles.append(self.Vehicle(lines[i+1]))
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
    
    def move_vehicle(self, vehicle_index, vector):
        for i in range(abs(vector)):
            if not self.move_vehicle_by_one(vehicle_index, (vector > 0)):
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
                    self.occupied.add((v.x, v.y))
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
                    self.occupied.add((v.x, v.y))
                    v.y -= 1
        return True

    def is_solved(self):
        return self.vip.x + self.vip.size >= self.width

if __name__ == '__main__':
    board = Board(open('puzzle.txt').read())
    for move in open('log.txt'):
        if not move:
            break
        _, vehicle_index, vector = map(int, move.split(" "))
        if not board.move_vehicle(vehicle_index, vector):
            return False
    print(board.is_solved())
