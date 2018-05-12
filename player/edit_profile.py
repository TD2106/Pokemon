from network.network_communication import send_message, receive_message
from player.player import Player


class EditPlayerProfile:
    def __init__(self, sock):
        self.sock = sock
        self.address_player = {}
        self.pokemon_count = {}

    def add_player(self, address, username):
        self.address_player[address] = Player(username)
        send_message(self.address_player[address].get_pokemon_info(), address, self.sock)
        self.pokemon_count[address], message = self.address_player[address].get_number_of_each_pokemon()
        send_message(message, address, self.sock)

    def listen(self):
        command, address = receive_message(self.sock)
        if command == "merge":
            self.address_player[address].merge_all_similar_pokemon(self.pokemon_count[address])
            self.address_player[address].save_progress()
            send_message(self.address_player[address].get_pokemon_info(), address, self.sock)
            self.address_player.pop(address)
            self.pokemon_count.pop(address)
        else:
            self.address_player.pop(address)
            self.pokemon_count.pop(address)
