import re
import socket
import sys
from random import randint

from network.network_communication import send_message, receive_message

listening_port = 100
pokecat_port = 101


def pokecat_client():
    print("Welcome to pokecat. You can travel using keys: a w s d for left, up, down, right.\n"
          "You are the X in the mini-map, O are pokemons. Input quit to quit game.")
    mini_map = receive_message(sock)[0]
    print(mini_map)
    while True:
        while True:
            command = input("")
            if command == "quit" or re.match("^[awsd]$", command):
                break
        send_message(command, ("localhost", pokecat_port), sock)
        if command != "quit":
            result = receive_message(sock)[0]
            print(result)
            mini_map = receive_message(sock)[0]
            print(mini_map)
        else:
            result = receive_message(sock)[0]
            print(result)
            break


def pokebat_client():
    print("Waiting for room...")
    number_of_poke, pokebat_server_address = receive_message(sock)
    number_of_poke = int(number_of_poke)
    poke_info = receive_message(sock)[0]
    print("Enter 3 distinct value from 0 to " + str(number_of_poke - 1) + "to choose pokemons")
    print(poke_info)
    indices = []
    while len(indices) < 3:
        try:
            num = int(input("Input " + str(len(indices) + 1) + " number from 0 - " + str(number_of_poke) + ": "))
            if num >= number_of_poke:
                print("Too big")
                pass
            elif num in indices:
                print("Exisited")
            else:
                indices.append(num)
        except ValueError:
            print("Incorrect format")
            pass
    result = ""
    for i in indices:
        result += str(i) + " "
    send_message(result, pokebat_server_address, sock)
    while True:
        turn = receive_message(sock)[0]
        print(turn)
        if turn == "Your turn":
            current_pokemon = receive_message(sock)[0]
            print(current_pokemon)
            current_opponent_pokemon = receive_message(sock)[0]
            print(current_opponent_pokemon)
            command = receive_message(sock)[0]
            print(command)
            if command == "You need to swich pokemon. Current one is dead.":
                switchable = receive_message(sock)[0]
                print(switchable)
                swap_idx = input("Input the pokemon you want to swap: ")
                send_message(swap_idx, pokebat_server_address, sock)
                result = receive_message(sock)[0]
                print(result)
            else:
                move = input("Enter your move. attack or switch: ")
                send_message(move, pokebat_server_address, sock)
                if move == "switch":
                    switchable = receive_message(sock)[0]
                    print(switchable)
                    swap_idx = input("Input the pokemon you want to swap: ")
                    send_message(swap_idx, pokebat_server_address, sock)
                    result = receive_message(sock)[0]
                    print(result)
                else:
                    result = receive_message(sock)[0]
                    print(result)
        elif turn == "Your opponent's turn":
            current_pokemon = receive_message(sock)[0]
            print(current_pokemon)
            result = receive_message(sock)[0]
            print(result)
        else:
            break


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port = randint(0, 65535)
try:
    sock.bind(("localhost", port))
except socket.error:
    print("Error creating socket")
    sys.exit()
print("Client started on port " + str(port))
send_message("Please provide socket", ("localhost", listening_port), sock)
data = receive_message(sock)[0]
verification_port = int(data)
server_address = ("localhost", verification_port)
option = input("1 for register. 2 for login: ")
send_message(option, ("localhost", verification_port), sock)
while True:
    user_name = input("Input user name: ")
    password = input("Input password: ")
    send_message(user_name, ("localhost", verification_port), sock)
    send_message(password, ("localhost", verification_port), sock)
    respond = receive_message(sock)[0]
    print(respond)
    if respond == "Success":
        break
option = input("1 for pokecat. 2 for pokebat. 3 for something. quit for exit: ")
send_message(option, ("localhost", verification_port), sock)
if option == '1':
    pokecat_client()
elif option == '2':
    pokebat_client()
elif option == 'quit':
    pass
