import queue
import re
import time
from random import randint
from threading import Thread

from network.network_communication import send_message, receive_message
from player.player import Player


class PokeCat:
    def __init__(self, sock, number_of_pokemon, pokemons_dicts):
        self.sock = sock
        self.ip_players = {}
        self.world_size = 1000
        self.world_map = [[0 for x in range(self.world_size)] for y in range(self.world_size)]
        self.pokemon_locations = set()
        self.number_of_spawn = 50000
        self.number_of_pokemon = number_of_pokemon
        self.pokemons_dicts = pokemons_dicts
        self.player_locations = {}
        self.mini_map_radius = 3
        self.pokemon_live_time = 600
        self.queue = queue.Queue()

    def spawn(self):
        print("Spawning pokemon")
        while len(self.pokemon_locations) < self.number_of_spawn:
            x = randint(0, self.world_size - 1)
            y = randint(0, self.world_size - 1)
            if (x, y) not in self.pokemon_locations:
                self.pokemon_locations.add((x, y))
                id = randint(1, self.number_of_pokemon + 1)
                self.world_map[x][y] = id
        print("Spawning done")

    def despawn(self):
        print("Despawning pokemon")
        while len(self.pokemon_locations) > 0:
            location = self.pokemon_locations.pop()
            self.world_map[location[0]][location[1]] = 0
        print("Despawning done")

    def is_player_not_in_location(self, location):
        for key, value in self.player_locations.items():
            if location == value:
                return False
        return True

    def add_player(self, address, user_name):
        self.ip_players[address] = Player(user_name)
        while True:
            x = randint(0, self.world_size)
            y = randint(0, self.world_size)
            if self.world_map[x][y] == 0 and self.is_player_not_in_location((x, y)):
                self.player_locations[address] = (x, y)
                break
        send_message(address=address, sock=self.sock, message=self.player_status(address))

    def is_valid(self, location):
        if location[0] < 0 or location[1] < 0 or location[0] > self.world_size or location[1] > self.world_size:
            return False
        else:
            return True

    def player_move(self, address, move):
        x = self.player_locations[address][0]
        y = self.player_locations[address][1]
        if move == 'a':
            y -= 1
        elif move == 's':
            x += 1
        elif move == 'd':
            y += 1
        elif move == 'w':
            x -= 1
        else:
            return "Invalid move"
        if not self.is_valid((x, y)):
            return "Can't move to location outside of the map"
        if self.is_player_not_in_location((x, y)):
            self.player_locations[address] = (x, y)
            if self.world_map[x][y] != 0:
                self.ip_players[address].add_pokemon(self.pokemons_dicts[self.world_map[x][y] - 1])
                result = "You move to location " + str((x, y)) + "and captured " + \
                         str(self.pokemons_dicts[self.world_map[x][y] - 1]["name"])
                self.world_map[x][y] = 0
            else:
                result = "You move location " + str((x, y))
        else:
            result = "Can't move to location. Occupied by other players"
        return result

    def player_status(self, address):
        x1 = max(0, self.player_locations[address][0] - self.mini_map_radius)
        x2 = min(self.world_size - 1, self.player_locations[address][0] + self.mini_map_radius)
        y1 = max(0, self.player_locations[address][1] - self.mini_map_radius)
        y2 = min(self.world_size - 1, self.player_locations[address][1] + self.mini_map_radius)
        result = "You are at " + str(self.player_locations[address]) + "\n"
        for i in range(x1, x2 + 1):
            for j in range(y1, y2 + 1):
                if (i, j) == self.player_locations[address]:
                    result += "X"
                elif self.world_map[i][j] != 0:
                    result += "O"
                else:
                    result += "-"
            result += "\n"
        return result

    def allocate_pokemon(self):
        while True:
            next_spawn = time.time() + self.pokemon_live_time
            self.queue.put((1,))
            while time.time() < next_spawn:
                time.sleep(30)
            self.queue.put((2,))

    def queue_handling(self):
        while True:
            if self.queue.not_empty:
                tup = self.queue.get()
                if tup[0] == 1:
                    self.spawn()
                elif tup[0] == 2:
                    self.despawn()
                elif tup[0] == 3:
                    send_message(self.player_move(tup[2], tup[1]), tup[2], self.sock)
                elif tup[0] == 4:
                    send_message(self.player_status(tup[1]), tup[1], self.sock)

    def execute_game(self):
        thread1 = Thread(target=self.allocate_pokemon, args=())
        thread1.start()
        thread2 = Thread(target=self.queue_handling, args=())
        thread2.start()
        while True:
            data, address = receive_message(sock=self.sock)
            if data == "quit":
                self.ip_players[address].save_progress()
                send_message("Save success", address, self.sock)
                self.ip_players.pop(address, None)
                self.player_locations.pop(address, None)
            elif re.match('^[asdw]$', data):
                self.queue.put((3, data, address))
                self.queue.put((4, address))
