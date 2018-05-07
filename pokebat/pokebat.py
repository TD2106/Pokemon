import sys

from network.network_communication import send_message, receive_message
from pokemon.pokemon import Pokemon


class PokebatRoom:
    def __init__(self, player_one, player_two, sock, player_one_address, player_two_address, ):
        self.players = []
        self.players_address = []
        self.players.append(player_one)
        self.players.append(player_two)
        self.sock = sock
        self.players_address.append(player_one_address)
        self.players_address.append(player_two_address)

    def check_lost(self, chosen_pokemons):
        for pokemon in chosen_pokemons:
            if not pokemon.is_lost():
                return False
        return True

    def end_game(self, won_idx, lost_idx, player_chosen_pokemons):
        total_exp = 0
        for pokemon in player_chosen_pokemons[lost_idx]:
            total_exp += pokemon.info["current_exp"]
            pokemon.prepare_for_storing()
        for pokemon in player_chosen_pokemons[won_idx]:
            pokemon.add_exp(total_exp // 3)
            pokemon.prepare_for_storing()
        self.players[0].save_progress()
        self.players[1].save_progress()
        send_message("You won", self.players_address[won_idx], self.sock)
        send_message("You lost", self.players_address[lost_idx], self.sock)
        self.sock.close()
        sys.exit()

    def battle_preparation(self, player_chosen_pokemons):
        for i in range(0, 2):
            send_message(message=str(len(self.players[i].player_info["pokemons_info"])),
                         address=self.players_address[i],
                         sock=self.sock)
            send_message(message=self.players[i].get_pokemon_info(), address=self.players_address[i], sock=self.sock)
        count = 0
        while count < 2:
            data, address = receive_message(self.sock)
            index = [int(x) for x in data.split()]
            pokemons = []
            if address == self.players_address[0]:
                for i in index:
                    pokemon = Pokemon(self.players[0].player_info["pokemons_info"][i])
                    pokemon.prepare_battle()
                    pokemons.append(pokemon)
                player_chosen_pokemons[0] = pokemons
            else:
                for i in index:
                    pokemon = Pokemon(self.players[1].player_info["pokemons_info"][i])
                    pokemon.prepare_battle()
                    pokemons.append(pokemon)
                player_chosen_pokemons[1] = pokemons
            count += 1
        player_chosen_pokemons[0].sort(key=lambda k: k.info['current_speed'], reverse=True)
        player_chosen_pokemons[1].sort(key=lambda k: k.info['current_speed'], reverse=True)

    def get_switchable_pokemons(self, player_chosen_pokemons, player_turn):
        result = ""
        for i in range(1, 3):
            if not player_chosen_pokemons[player_turn][i].is_lost():
                result += "Enter " + str(i) + " to switch with " + player_chosen_pokemons[player_turn][i].info[
                    "name"] + ".\n"
        if result == "":
            result = "You can't switch pokemon because there are none left. You lost a turn"
        return result

    def play_turn(self, player_turn, player_chosen_pokemons):
        opponent = (player_turn + 1) % 2
        send_message("Your turn", self.players_address[player_turn], self.sock)
        send_message("Your opponent's turn", self.players_address[opponent], self.sock)
        for i in range(0, 2):
            send_message("Your current pokemon is: " + player_chosen_pokemons[i][0].info["name"],
                         self.players_address[i], self.sock)
        send_message("The opponent current pokemon is: " + player_chosen_pokemons[opponent][0].info["name"],
                     self.players_address[player_turn], self.sock)
        if player_chosen_pokemons[player_turn][0].is_lost():
            send_message("You need to switch pokemon. Current one is dead. Or you can quit",
                         self.players_address[player_turn],
                         self.sock)
            command = receive_message(self.sock)[0]
            if command == "quit":
                send_message("Your opponent quit", self.players_address[opponent], self.sock)
                self.end_game(opponent, player_turn, player_chosen_pokemons)
            message = self.get_switchable_pokemons(player_chosen_pokemons, player_turn)
            send_message(message, self.players_address[player_turn], self.sock)
            swap_idx = int(receive_message(self.sock)[0])
            if not player_chosen_pokemons[player_turn][swap_idx].is_lost():
                player_chosen_pokemons[player_turn][0], player_chosen_pokemons[player_turn][swap_idx] = \
                    player_chosen_pokemons[player_turn][swap_idx], player_chosen_pokemons[player_turn][0]
                send_message("Successful switch", self.players_address[player_turn], self.sock)
            else:
                send_message("Unsuccessful switch", self.players_address[player_turn], self.sock)
            send_message("Your opponent choose switch", self.players_address[opponent], self.sock)
        else:
            send_message("You can attack or switch or quit current pokemon.", self.players_address[player_turn],
                         self.sock)
            command = receive_message(self.sock)[0]
            if command == 'attack':
                dmg = player_chosen_pokemons[player_turn][0].attack_other_pokemon(player_chosen_pokemons[opponent][0])
                send_message("You caused " + str(dmg) + " to opponent current pokemon",
                             self.players_address[player_turn], self.sock)
                send_message("Your current pokemon received a damage of " + str(dmg),
                             self.players_address[opponent], self.sock)
            elif command == 'switch':
                message = self.get_switchable_pokemons(player_chosen_pokemons, player_turn)
                send_message(message, self.players_address[player_turn], self.sock)
                if message == "You can't switch pokemon because there are none left. You lost a turn":
                    pass
                else:
                    swap_idx = int(receive_message(self.sock)[0])
                    if not player_chosen_pokemons[player_turn][swap_idx].is_lost():
                        player_chosen_pokemons[player_turn][0], player_chosen_pokemons[player_turn][swap_idx] = \
                            player_chosen_pokemons[player_turn][swap_idx], player_chosen_pokemons[player_turn][0]
                        send_message("Successful switch", self.players_address[player_turn], self.sock)
                    else:
                        send_message("Unsuccessful switch", self.players_address[player_turn], self.sock)
                send_message("Your opponent choose switch", self.players_address[opponent], self.sock)
            elif command == 'quit':
                send_message("Your opponent quit", self.players_address[opponent], self.sock)
                self.end_game(opponent, player_turn, player_chosen_pokemons)

    def execute(self):
        player_chosen_pokemons = [None] * 2
        self.battle_preparation(player_chosen_pokemons)
        turn = 0
        while not self.check_lost(player_chosen_pokemons[0]) and not self.check_lost(player_chosen_pokemons[1]):
            self.play_turn(turn % 2, player_chosen_pokemons)
            turn += 1
        if self.check_lost(player_chosen_pokemons[0]):
            self.end_game(1, 0, player_chosen_pokemons)
        else:
            self.end_game(0, 1, player_chosen_pokemons)
