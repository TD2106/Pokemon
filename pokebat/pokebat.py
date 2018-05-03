from network.network_communication import send_message, receive_message
from pokemon.pokemon import Pokemon


class PokebatRoom:
    def __init__(self, player_one, player_two, sock, player_one_address, player_two_address):
        self.player_one = player_one
        self.player_two = player_two
        self.sock = sock
        self.player_one.prepare_for_battle()
        self.player_two.prepare_for_battle()
        self.player_one_address = player_one_address
        self.player_two_address = player_two_address

    def check_lost(self, chosen_pokemons):
        for pokemon in chosen_pokemons:
            if not pokemon.is_lost():
                return False
        return True

    def win(self, won_pokemon, lost_pokemon):
        total_exp = 0
        for pokemon in lost_pokemon:
            total_exp += pokemon.info["current_exp"]
            pokemon.prepare_for_storing()
        for pokemon in won_pokemon:
            pokemon.add_exp(total_exp // 3)
            pokemon.prepare_for_storing()
        self.player_one.save_progress()
        self.player_two.save_progress()

    def execute(self):
        count = 0
        send_message(message=str(len(self.player_one.info["pokemons_info"])), address=self.player_one_address,
                     sock=self.sock)
        send_message(message=str(len(self.player_two.info["pokemons_info"])), address=self.player_two_address,
                     sock=self.sock)
        send_message(message=self.player_one.get_pokemon_info(), address=self.player_one_address, sock=self.sock)
        send_message(message=self.player_two.get_pokemon_info(), address=self.player_two_address, sock=self.sock)
        player_one_chosen_pokemons = []
        player_two_chosen_pokemons = []
        while count < 2:
            data, address = receive_message(self.sock)
            index = [int(x) for x in data.split(" ")]
            if address == self.player_one_address:
                for i in index:
                    pokemon = Pokemon(self.player_one.info["pokemons_info"][i])
                    pokemon.prepare_battle()
                    player_one_chosen_pokemons.append(pokemon)
            else:
                for i in index:
                    pokemon = Pokemon(self.player_two.info["pokemons"][i])
                    pokemon.prepare_battle()
                    player_two_chosen_pokemons.append(pokemon)
            count += 1
        player_one_chosen_pokemons.sort(key=lambda k: k['current_speed'], reverse=True)
        player_two_chosen_pokemons.sort(key=lambda k: k['current_speed'], reverse=True)
