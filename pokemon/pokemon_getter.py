import json

from pokemon.pokemon import Pokemon


def get_all_base_pokemon():
    with open("../json/PokemonBase.json", "r") as file:
        pokemon_dicts = json.load(file)
    pokemons = []
    for dict in pokemon_dicts:
        pokemons.append(Pokemon(dict))
    return pokemons
