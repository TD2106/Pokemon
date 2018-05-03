import socket
import time
from random import randint
from threading import Thread

from network.network_communication import send_message, receive_message
from player.player import Player
from pokecat.pokecat import PokeCat
from pokemon.pokemon import Pokemon

listening_port = 100
pokecat_port = 101

def handle_client_verification(private_socket, client_address):
    option = receive_message(private_socket)[0]
    exit_time = time.time() + 120
    if option == '1':
        while True:
            if exit_time == time.time():
                return
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
            if exit_time == time.time():
                return
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
        pass
    elif option == '3':
        pass
    private_socket.close()


listening_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
pokecat_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listening_sock.bind(("localhost", listening_port))
pokecat_sock.bind(("localhost", pokecat_port))
pokemons_dicts = Pokemon.get_all_base_pokemon_dicts()
pokecat_instance = PokeCat(pokecat_sock, len(pokemons_dicts), pokemons_dicts)
pokecat_thread = Thread(target=pokecat_instance.execute_game, args=())
pokecat_thread.start()
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
