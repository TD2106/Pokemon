import copy
import json
import os
from pathlib import Path

from pokemon.pokemon import Pokemon

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
        self.player_info["pokemons_info"].append(copy.deepcopy(pokemon_info))

    def prepare_for_battle(self):
        self.player_info["pokemons"] = []
        for pokemon_info in self.player_info["pokemons_info"]:
            self.player_info["pokemons"].append(Pokemon(pokemon_info))

    def save_progress_pokecat(self):
        self.player_info.pop("pokemons", None)
        with open(self.json_path, "w") as user_json:
            json.dump(self.player_info, user_json, indent=2)
