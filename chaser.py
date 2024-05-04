

import pygame
import math
import argparse
from random import randrange, choice
from time import sleep
from collections import deque, defaultdict


def euclidean(from_x, from_y, to_x, to_y):
    
    return math.sqrt((to_x - from_x) ** 2 + (to_y - from_y) ** 2)


class Cell:
    def __init__(self, xy_cords, size):
        
        self.x = xy_cords[0]
        self.y = xy_cords[1]
        self.size = size
        self.color = (0, 0, 0)
        self.shape = pygame.Rect(self.x, self.y, self.size, self.size)

    def up(self, val):
        
        self.y -= val
        self.shape = pygame.Rect(self.x, self.y, self.size, self.size)

    def down(self, val):
        
        self.y += val
        self.shape = pygame.Rect(self.x, self.y, self.size, self.size)

    def left(self, val):
        
        self.x -= val
        self.shape = pygame.Rect(self.x, self.y, self.size, self.size)

    def right(self, val):
        
        self.x += val
        self.shape = pygame.Rect(self.x, self.y, self.size, self.size)


class Player(Cell):
    def __init__(self, xy_cords, size):
        
        super().__init__(xy_cords, size)
        self.color = (0, 0, 255)


class Zombie(Cell):
    def __init__(self, xy_cords, size):
        
        super().__init__(xy_cords, size)
        self.color = (0, 255, 0)

    def euclidean_find(self, player_obj, val):
        
        p_x, p_y = player_obj.x, player_obj.y
        moves = [("n", euclidean(self.x, self.y - val, p_x, p_y)), ("s", euclidean(self.x, self.y + val, p_x, p_y)),
                 ("e", euclidean(self.x + val, self.y, p_x, p_y)), ("w", euclidean(self.x - val, self.y, p_x, p_y))]
        return min(moves, key=lambda x: x[1])[0]


class Wall(Cell):
    def __init__(self, xy_cords, size):
        super().__init__(xy_cords, size)
        self.color = (255, randrange(100, 200), 0)


class Game:
    def __init__(self, n, m, cell_size, line_size):
       
        pygame.init()
        self.n = n
        self.m = m
        self.cell_width = cell_size
        self.line_width = line_size
        self.total_height = self.n * self.cell_width + (self.n + 1) * self.line_width
        self.total_width = self.m * self.cell_width + (self.m + 1) * self.line_width
        self.screen = pygame.display.set_mode((self.total_width, self.total_height))
        self.player = None
        self.walls = {}
        self.zombies = {}

    def get_xy_cords(self, cords):
       
        n, m = cords
        x = (m + 1) * self.line_width + m * self.cell_width
        y = (n + 1) * self.line_width + n * self.cell_width
        return x, y

    def get_nm_cords(self, xy_cords):
        
        x, y = xy_cords
        n = (y - self.line_width) / (self.line_width + self.cell_width)
        m = (x - self.line_width) / (self.line_width + self.cell_width)
        return int(n), int(m)

    def add_player(self, cords):
        
        xy_cords = self.get_xy_cords(cords)
        player = Player(xy_cords, self.cell_width)
        self.player = player

    def add_wall(self, cords):
        
        xy_cords = self.get_xy_cords(cords)
        wall = Wall(xy_cords, self.cell_width)
        self.walls[cords] = wall

    def add_zombie(self, cords):
        
        xy_cords = self.get_xy_cords(cords)
        zombie = Zombie(xy_cords, self.cell_width)
        self.zombies[cords] = zombie

    def set_up(self):
        
        if self.line_width % 2:  # even parity quick fix
            start = self.line_width // 2
        else:
            start = self.line_width // 2 - 1

        for y in range(start, self.total_height, self.cell_width + self.line_width):
            pygame.draw.line(self.screen, "white", (0, y),
                             (self.total_width, y), self.line_width)
        for x in range(start, self.total_width, self.cell_width + self.line_width):
            pygame.draw.line(self.screen, "white", (x, 0),
                             (x, self.total_height), self.line_width)

        if self.player is not None:
            pygame.draw.rect(self.screen, self.player.color, self.player.shape)
        if len(self.walls):
            for wall_obj in self.walls.values():
                pygame.draw.rect(self.screen, wall_obj.color, wall_obj.shape)
        if len(self.zombies):
            for zombie_obj in self.zombies.values():
                pygame.draw.rect(self.screen, zombie_obj.color, zombie_obj.shape)

    def clear(self, cords):
       
        xy_cords = self.get_xy_cords(cords)
        black_cell = Cell(xy_cords, self.cell_width)
        pygame.draw.rect(self.screen, black_cell.color, black_cell.shape)

    def get_neighbours(self, cords, r=0):
        
        n, m = cords
        output = []
        if (n - 1 - r, m) not in self.walls and n - 1 - r >= 0:
            output.append([(n - 1 - r, m) for r in range(r + 1)]) if r else output.append((n - 1, m))
        if (n + 1 + r, m) not in self.walls and n + 1 + r <= self.n - 1:
            output.append([(n + 1 + r, m) for r in range(r + 1)]) if r else output.append((n + 1, m))
        if (n, m - 1 - r) not in self.walls and m - 1 - r >= 0:
            output.append([(n, m - 1 - r) for r in range(r + 1)]) if r else output.append((n, m - 1))
        if (n, m + 1 + r) not in self.walls and m + 1 + r <= self.m - 1:
            output.append([(n, m + 1 + r) for r in range(r + 1)]) if r else output.append((n, m + 1))
        return output

    def find_path(self, src, trg):
        
        src_n, src_m = src
        trg_n, trg_m = trg
        queue = deque([(src_n, src_m)])
        previous = {(src_n, src_m): (src_n, src_m)}
        while queue:
            curr_cords = queue.popleft()
            for child in self.get_neighbours(curr_cords):
                if child not in previous:
                    previous[child] = curr_cords
                    queue.append(child)
                if child == (trg_n, trg_m):
                    return previous

    def get_moves(self, src_obj, trg_obj):
        
        src = self.get_nm_cords((src_obj.x, src_obj.y))
        trg = self.get_nm_cords((trg_obj.x, trg_obj.y))
        previous_data = self.find_path(src, trg)
        moves = []
        prev = None
        while prev != src:
            prev = previous_data[trg]
            diff_n, diff_m = trg[0] - prev[0], trg[1] - prev[1]
            if diff_m == 1:
                moves.append("e")
            elif diff_m == -1:
                moves.append("w")
            elif diff_n == 1:
                moves.append("s")
            elif diff_n == -1:
                moves.append("n")
            trg = prev
        return moves[::-1]

    def can_go_direction(self, cords, direction):
        
        n, m = cords
        if direction == "n" and n != 0 and (n - 1, m) not in self.walls:
            return True
        elif direction == "s" and n != self.n - 1 and (n + 1, m) not in self.walls:
            return True
        elif direction == "e" and m != self.m - 1 and (n, m + 1) not in self.walls:
            return True
        elif direction == "w" and m != 0 and (n, m - 1) not in self.walls:
            return True
        return False

    def get_maze_cords(self):
        
        cords = self.get_nm_cords((self.player.x, self.player.y))
        stack = [cords]
        is_wall = defaultdict(lambda: True)
        while stack:
            current_cell_cords = stack.pop()
            neighbours = [neighbour for neighbour in self.get_neighbours(current_cell_cords, 1)
                          if is_wall[neighbour[1]]]
            if neighbours:
                stack.append(current_cell_cords)
                between_cell, chosen_cell = choice(neighbours)
                is_wall[between_cell] = False
                is_wall[chosen_cell] = False
                stack.append(chosen_cell)
        return is_wall

    def generate_maze(self):
       
        walls = self.get_maze_cords()
        for n in range(self.n):
            for m in range(self.m):
                if walls[n, m]:
                    self.add_wall((n, m))

    def get_unoccupied_cords(self):
       
        output = []
        for n in range(self.n):
            for m in range(self.m):
                if (n, m) not in self.walls:
                    output.append((n, m))
        return output

    def get_random_unoccupied_cords(self):
        
        return choice(self.get_unoccupied_cords())

    def move(self, obj, direction):
        
        x, y = obj.x, obj.y
        cords = self.get_nm_cords((x, y))
        val = self.cell_width + self.line_width
        self.clear(cords)
        if direction == "n" and self.can_go_direction(cords, "n"):
            obj.up(val)
        elif direction == "s" and self.can_go_direction(cords, "s"):
            obj.down(val)
        elif direction == "e" and self.can_go_direction(cords, "e"):
            obj.right(val)
        elif direction == "w" and self.can_go_direction(cords, "w"):
            obj.left(val)
        pygame.draw.rect(self.screen, obj.color, obj.shape)

    def run(self):
        
        self.set_up()
        running = True
        direction = None
        slower = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        direction = "n"
                    elif event.key == pygame.K_s:
                        direction = "s"
                    elif event.key == pygame.K_d:
                        direction = "e"
                    elif event.key == pygame.K_a:
                        direction = "w"
                elif event.type == pygame.KEYUP:
                    direction = None
            if direction is not None:
                self.move(self.player, direction)
            slower = not slower
            if slower:  # so that zombie will move two times slower than player
                for zombie in self.zombies.values():
                    if (zombie.x, zombie.y) != (self.player.x, self.player.y):
                        zombie_direction = self.get_moves(zombie, self.player)
                        # zombie_direction = zombie.euclidean_find(self.player, self.cell_width + self.line_width)
                        self.move(zombie, zombie_direction[0])
            pygame.display.update()
            sleep(0.1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("window_parameters", help="Game parameters: (width_cells_amount, "
                                                  "height_cells_amount, cell_width, line_width)", nargs="+", type=int)
    parser.add_argument("-p", "--player_cords", help="Starting player coordinates: (n, m)",
                        default=(0, 0), nargs="+", type=int)
    parser.add_argument("-z", "--zombie_amount", help="Amount of zombies in the game", default=1, type=int)
    args = parser.parse_args()
    total_height, total_width, cell_width, line_width = args.window_parameters
    player_cords = args.player_cords
    zombie_amount = args.zombie_amount
    s1 = Game(total_height, total_width, cell_width, line_width)  # total height, total width, cell_width, line_width
    s1.add_player(tuple(player_cords))
    s1.generate_maze()
    for i in range(zombie_amount):
        s1.add_zombie(s1.get_random_unoccupied_cords())
    s1.run()


if __name__ == '__main__':
    main()
