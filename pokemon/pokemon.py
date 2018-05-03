import json
import os
import random

path = os.getcwd()


class Pokemon:
    @staticmethod
    def get_all_base_pokemon_dicts():
        with open(str(path) + "\\json" + "\\" + "PokemonBase.json", "r") as file:
            pokemon_dicts = json.load(file)
        return pokemon_dicts

    def __init__(self, poke_info):
        self.info = poke_info

    def level_up(self):
        while self.info["base_exp"] * 2 <= self.info["current_exp"]:
            self.info["base_exp"] *= 2
            self.info["level"] += 1
            self.info["current_hp"] = int((1 + self.info["EV"]) * self.info["current_hp"])
            self.info["current_attack"] = int((1 + self.info["EV"]) * self.info["current_attack"])
            self.info["current_defense"] = int((1 + self.info["EV"]) * self.info["current_defense"])
            self.info["current_sp_attack"] = int((1 + self.info["EV"]) * self.info["current_sp_attack"])
            self.info["current_sp_defense"] = int((1 + self.info["EV"]) * self.info["current_sp_defense"])

    def add_exp(self, added_exp):
        self.info["current_exp"] += added_exp
        self.level_up()

    def get_info(self):
        result = ""
        for key, value in self.info.items():
            result += key + " " + str(value) + "\n"
        return result

    def take_damage(self, dmg):
        self.info["current_battle_hp"] -= dmg

    def is_lost(self):
        return self.info["current_battle_hp"] <= 0

    def attack_other_pokemon(self, other):
        attack_type = random.randint(0, 1)
        if attack_type == 0:
            dmg = max(0, self.info["current_attack"] - other.info["current_defense"])
            other.take_damage(dmg)
        else:
            dmg = max(0,
                      int(self.info["current_sp_atk"] * self.get_max_multiplier(other)) - other.info["current_sp_def"])
            other.take_damage(dmg)

    def get_max_multiplier(self, other):
        result = 0.0
        for key, value in self.info["attack_dmg_multiplier"].items():
            if key in other.info["types"]:
                result = max(result, value)
        if result == 0.0:
            result = 1.0
        return result

    def prepare_battle(self):
        self.info["current_battle_hp"] = self.info["current_hp"]

    def prepare_for_storing(self):
        self.info.pop("current_battle_hp", None)
