import copy
import json
import os
import random
from pathlib import Path
path = os.getcwd()


class Player:
    @staticmethod
    def is_login_correct(user_name, password):
        if Player.is_user_name_exist(user_name):
            with open(str(path) + "\\json" + "\\" + user_name + ".json", "r") as user_json:
                player_info = json.load(user_json)
                if player_info["password"] == password:
                    return True
                else:
                    return False
        else:
            return False

    @staticmethod
    def is_user_name_exist(user_name):
        user_json = Path(str(path) + "\\json" + "\\" + user_name + ".json")
        return user_json.is_file()

    @staticmethod
    def add_user(user_name, password):
        player_info = dict(user_name=user_name, password=password, pokemons_info=[])
        with open(str(path) + "\\json" + "\\" + user_name + ".json", "w") as user_json:
            json.dump(player_info, user_json, indent=2)

    def __init__(self, user_name):
        self.json_path = str(path) + "\\json" + "\\" + user_name + ".json"
        with open(self.json_path, "r") as user_json:
            self.player_info = json.load(user_json)

    def add_pokemon(self, pokemon_info):
        pokemon_info_copy = copy.deepcopy(pokemon_info)
        pokemon_info_copy["EV"] = round(random.uniform(0.5, 1), 2)
        self.player_info["pokemons_info"].append(pokemon_info_copy)

    def save_progress(self):
        with open(self.json_path, "w") as user_json:
            json.dump(self.player_info, user_json, indent=2)

    def get_pokemon_info(self):
        result = "Your pokemons are:\n"
        result += json.dumps(self.player_info["pokemons_info"], indent=2)
        return result

    def get_number_of_each_pokemon(self):
        pokemon_count = {}
        for info in self.player_info["pokemons_info"]:
            if info["name"] in pokemon_count:
                pokemon_count[info["name"]] += 1
            else:
                pokemon_count[info["name"]] = 1
        for key, value in pokemon_count.items():
            print(key + ":" + str(value))
