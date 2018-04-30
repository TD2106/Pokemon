from selenium.webdriver import Chrome, ChromeOptions
from bs4 import BeautifulSoup
from crawler.bulbagarden_crawler import BulbGardenCrawler


class PokedexCrawler:
    def __init__(self):
        home_page = "https://www.pokedex.org/"
        options = ChromeOptions()
        options.add_argument("headless")
        self.browser = Chrome(options=options)
        self.browser.get(home_page)
        self.number_of_pokemon = self.browser.execute_script("return document.getElementById('monsters-list')."
                                                            "getElementsByTagName('li').length")
        self.bulb_garden_crawler = BulbGardenCrawler()

    def get_pokemon(self):
        self.bulb_garden_crawler.get_page()
        pokemon_url = "https://www.pokedex.org/#/pokemon/"
        for i in range(1, self.number_of_pokemon + 1):
            print("Downloading pokemon: id = " + str(i))
            pokemon_information = {}
            self.browser.get(pokemon_url + str(i))
            html_page = self.browser.page_source
            soup = BeautifulSoup(html_page, 'html.parser')
            pokemon_information["id"] = i
            pokemon_information["name"] = soup.find('h1', {"class": "detail-panel-header"}).text
            types = []
            for value in soup.find("div", {"class": "detail-types"}).find_all("span",{"class": "monster-type"}.items()):
               types.append(value.text)
            pokemon_information["types"] = types
            for row in soup.find_all("div", {"class": "detail-stats-row"}):
                stat_name = row.find("span").text
                stat_name = "base_"+stat_name.lower().replace(" ", "_")
                pokemon_information[stat_name] = int(row.find("div", {"class": "stat-bar-fg"}).text)
            attack_dmg_multiplier = {}
            for row in soup.find_all("div", {"class": "when-attacked-row"}):
                while len(row.contents):
                    if len(row.find("span", {"class": "monster-multiplier"}).text.replace("x","")) > 0:
                        attack_dmg_multiplier[row.find("span", {"class": "monster-type"}).text] = \
                            float(row.find("span", {"class": "monster-multiplier"}).text.replace("x",""))
                    row.find("span", {"class": "monster-type"}).decompose()
                    row.find("span", {"class": "monster-multiplier"}).decompose()
            pokemon_information["attack_dmg_multiplier"] = attack_dmg_multiplier
            pokemon_information["base_exp"] = self.bulb_garden_crawler.get_base_exp(i)
            print("Download complete")
        self.browser.quit()

test = PokedexCrawler()
test.get_pokemon()