import queue
import socket
from random import randint
from threading import Thread

from network.network_communication import send_message, receive_message
from player.player import Player
from pokebat.pokebat import PokebatRoom
from pokecat.pokecat import PokeCat
from pokemon.pokemon import Pokemon

listening_port = 100
pokecat_port = 101

def handle_client_verification(private_socket, client_address):
    option = receive_message(private_socket)[0]
    if option == '1':
        while True:
            user_name = receive_message(private_socket)[0]
            password = receive_message(private_socket)[0]
            if Player.is_user_name_exist(user_name) or user_name == "":
                send_message("Choose another user name. Already exists or blank.", client_address, private_socket)
            else:
                Player.add_user(user_name, password)
                send_message("Success", client_address, private_socket)
                print(user_name + " registered and login successfully")
                break
    elif option == '2':
        while True:
            user_name = receive_message(private_socket)[0]
            password = receive_message(private_socket)[0]
            if Player.is_login_correct(user_name, password):
                send_message("Success", client_address, private_socket)
                print(user_name + " login successfully")
                break
            else:
                send_message("Incorrect", client_address, private_socket)
    option = receive_message(private_socket)[0]
    if option == '1':
        pokecat_instance.add_player(client_address, user_name)
    elif option == '2':
        player_queue.put(Player(user_name))
        player_address_queue.put(client_address)
    elif option == '3':
        pass
    private_socket.close()


def handle_player_queue_for_pokebat():
    while True:
        if player_queue.qsize() >= 2 and player_address_queue.qsize() >= 2:
            new_pokebat_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            while True:
                new_pokebat_port = randint(0, 65535)
                try:
                    new_pokebat_sock.bind(("localhost", new_pokebat_port))
                    break
                except socket.error:
                    pass
            new_pokebat_room = PokebatRoom(player_queue.get(), player_queue.get(), new_pokebat_sock,
                                           player_address_queue.get(), player_address_queue.get())
            new_pokebat_thread = Thread(target=new_pokebat_room.execute, args=())
            new_pokebat_thread.start()


player_queue = queue.Queue()
player_address_queue = queue.Queue()
listening_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
pokecat_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listening_sock.bind(("localhost", listening_port))
pokecat_sock.bind(("localhost", pokecat_port))
pokemons_dicts = Pokemon.get_all_base_pokemon_dicts()
pokecat_instance = PokeCat(pokecat_sock, len(pokemons_dicts), pokemons_dicts)
pokecat_thread = Thread(target=pokecat_instance.execute_game, args=())
pokecat_thread.start()
pokebat_thread = Thread(target=handle_player_queue_for_pokebat, args=())
pokebat_thread.start()
print("Server started on port 100")
while True:
    data, address = receive_message(listening_sock)
    print(str(address) + ":" + data)
    new_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    new_port = 0
    while True:
        new_port = randint(0, 65535)
        try:
            new_sock.bind(("localhost", new_port))
            break
        except socket.error:
            pass
    send_message(str(new_port), address, listening_sock)
    new_thread = Thread(target=handle_client_verification, args=(new_sock, address))
    new_thread.start()
