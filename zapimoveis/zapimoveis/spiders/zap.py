import scrapy
import scrapy_selenium
from bs4 import BeautifulSoup
import re


class ZapSpider(scrapy.Spider):
    name = "zap"
    allowed_domains = ["zapimoveis.com.br"]
    start_url = "http://zapimoveis.com.br/venda/casas/sc+florianopolis/"
    page = 1

    def start_requests(self):
        yield scrapy_selenium.SeleniumRequest(url=self.get_url(), callback=self.parse)

    def get_url(self):
        return self.start_url + "?pagina=" + str(self.page)

    def parse(self, response):

        # check if response status is 400
        if response.status >= 400:
            self.logger.warn(f"Reached last page: {self.page}")
            return

        # parse stuff
        for item in self.scrape_list_page(response):
            yield item

        # yield new pages
        self.page += 1
        yield scrapy_selenium.SeleniumRequest(url=self.get_url(), callback=self.parse)

    def scrape_list_page(self, response):
        soup = BeautifulSoup(response.body)
        container = soup.select(".js-results .card-container")
        for card in container:
            relevance = card.select_one(".simple-card__header .label__container")
            price = self.extract_number(card.select_one(".js-price"))
            iptu = self.extract_number(card.select_one(".iptu"))
            address = card.select_one(".simple-card__address")
            size = self.extract_number(card.select_one(".js-areas"))
            rooms = self.extract_number(card.select_one(".js-bedrooms"))
            garages = self.extract_number(card.select_one(".js-parking-spaces"))
            bathrooms = self.extract_number(card.select_one(".js-bathrooms"))

            yield {
                "request_url": response.url,
                "url": None,
                "price": price,
                "iptu": iptu,
                "address": address.text if address else None,
                "size": size,
                "rooms": rooms,
                "garages": garages,
                "bathroom": bathrooms,
                "agency": None,
                "type": "list",
                "relevance": relevance.text if relevance else None,
            }

    # @staticmethod
    # def magica(text):
    #     rgx = r"R\$ ?((?:\d*[.,]?)*)"
    #     match = re.search(rgx, text)
    #     if match:
    #         return match.group(1).strip()
    #     return "Alakazam hoje nao"

    @staticmethod
    def extract_number(text):
        if not text:
            return "not text"
        rgx = r"((?:\d+[.,]?)+)"
        match = re.search(rgx, text.text)
        if match:
            return match.group(1).strip()
        return "not match"
