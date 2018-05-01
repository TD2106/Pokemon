import json
from pathlib import Path


class Player:
    @staticmethod
    def is_login_correct(user_name, password):
        if Player.is_user_name_exist(user_name):
            with open("../json/" + user_name + ".json", "r") as user_json:
                player_info = json.load(user_json)
                if player_info["password"] == password:
                    return True
                else:
                    return False
        else:
            return False

    @staticmethod
    def is_user_name_exist(user_name):
        user_json = Path("../json/" + user_name + ".json")
        return user_json.is_file()

    @staticmethod
    def add_user(user_name, password):
        if Player.is_user_name_exist(user_name):
            return False
        else:
            player_info = dict(user_name=user_name, password=password, pokemons=[])
            with open("../json/" + user_name + ".json", "w") as user_json:
                json.dump(player_info, user_json)
            return True

    def __init__(self, user_name):
        self.json_path = "../json/" + user_name + ".json"
        with open(self.json_path, "r") as user_json:
            self.player_info = json.load(user_json)

    def add_pokemon(self, pokemon):
        self.player_info["pokemons"].append(pokemon)
