from selenium.webdriver import Chrome, ChromeOptions
from bs4 import BeautifulSoup

class BulbGardenCrawler:
    def __init__(self):
        options = ChromeOptions()
        options.add_argument("headless")
        self.browser = Chrome(options=options)
        self.url = "http://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_effort_value_yield"

    def get_page(self):
        self.browser.get(self.url)
        html_page = self.browser.page_source
        soup = BeautifulSoup(html_page, 'html.parser')
        self.table_body = soup.find("tbody")
        self.browser.quit()

    def get_base_exp(self, id):
        result = 0
        for row in self.table_body.find_all("tr"):
            id_string = row.find("b").text
            try:
                id_int = int(id_string)
                if id_int == id:
                    result = int(row.find("td",{"style": "background:#FFFFFF"}).text)
            except:
                pass
            finally:
                row.decompose()
            if result != 0:
                break
        return result
