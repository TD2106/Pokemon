import re
import time
from random import randint
from threading import Thread

from network.network_communication import send_message, receive_message
from player.player import Player


class PokeCat:
    def __init__(self, sock, number_of_pokemon, pokemons):
        self.sock = sock
        self.ip_players = {}
        self.world_size = 1000
        self.world_map = [[0 for x in range(self.world_size)] for y in range(self.world_size)]
        self.pokemon_locations = []
        self.number_of_spawn = 300
        self.number_of_pokemon = number_of_pokemon
        self.pokemons = pokemons
        self.player_locations = {}
        self.mini_map_radius = 3
        self.pokemon_live_time = 120

    def spawn(self):
        while len(self.pokemon_locations) < self.number_of_spawn:
            x = randint(0, self.world_size)
            y = randint(0, self.world_size)
            if (x, y) not in self.pokemon_locations:
                self.pokemon_locations.append((x, y))
                id = randint(1, self.number_of_pokemon + 1)
                self.world_map[x][y] = id

    def despawn(self):
        while len(self.pokemon_locations) > 0:
            location = self.pokemon_locations.pop()
            self.world_map[location[0]][location[1]] = 0

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
            x -= 1
        elif move == 's':
            y += 1
        elif move == 'd':
            x += 1
        elif move == 'w':
            y -= 1
        if not self.is_valid((x, y)):
            return "Can't move to location outside of the map"
        if self.is_player_not_in_location((x, y)):
            self.player_locations[address] = (x, y)
            if self.world_map[x][y] != 0:
                self.ip_players[address].add_pokemon(self.pokemons[self.world_map[x][y] - 1])
                result = "You are at location " + str((x, y)) + "and captured " + \
                         str(self.pokemons[self.world_map[x][y] - 1].info["name"])
                self.world_map[x][y] = 0
            else:
                result = "You are at location " + str((x, y))
        else:
            result = "Can't move to location. Occupied by other players"
        return result

    def player_status(self, address):
        x1 = max(0, self.player_locations[address][0] - self.mini_map_radius)
        x2 = min(self.world_size - 1, self.player_locations[address][0] + self.mini_map_radius)
        y1 = max(0, self.player_locations[address][1] - self.mini_map_radius)
        y2 = min(self.world_size - 1, self.player_locations[address][1] + self.mini_map_radius)
        result = "You are at " + self.player_locations[address] + "\n"
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
            self.spawn()
            while time.time() < next_spawn:
                pass
            self.despawn()

    def execute_game(self):
        thread1 = Thread(target=self.allocate_pokemon, args=())
        thread1.start()
        thread1.join()
        while True:
            data, address = receive_message(sock=self.sock)
            if data == "quit":
                self.ip_players.pop(address, None)
                self.player_locations.pop(address, None)
            elif re.match('^[asdw]$', data):
                send_message(self.player_move(address, data), address, self.sock)
                send_message(self.player_status(address), address, self.sock)
