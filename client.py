import re
import socket
import sys
from random import randint

from network.network_communication import send_message, receive_message

listening_port = 100
pokecat_port = 101
pokebat_port = 102
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
option = input("1 for pokecat. 2 for pokebat. 3 for something: ")
send_message(option, ("localhost", verification_port), sock)
if option == '1':
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
        result = receive_message(sock)[0]
        print(result)
        mini_map = receive_message(sock)[0]
        print(mini_map)
