# https://www.engineering.cornell.edu/faculty-directory?letter=A
import scrapy
from string import ascii_uppercase


class EngProfessorsListSpider(scrapy.Spider):
    name = "eng_professors_list"
    start_urls = [
        # "https://www.engineering.cornell.edu/faculty-directory?letter=W"
        f"https://www.engineering.cornell.edu/faculty-directory?letter={letter}"
        for letter in ascii_uppercase
    ]  # Replace with the actual URL

    def parse(self, response):
        cards = response.xpath(
            '//article[contains(@class, "person--listing faculty--listing")]//div[contains(@class, "row")]'
        )

        for card in cards:
            yield {
                "url": card.xpath(
                    './/div[contains(@class, "faculty-pic columns small-12 medium-12 large-12")]//a/@href'
                ).get(),
                "prof_name": card.xpath(
                    './/h2[contains(@class, "h3 person__name")]//a//span/text()'
                ).get(),
                "prof_img": card.xpath(
                    './/div[contains(@class, "faculty-pic columns small-12 medium-12 large-12")]//a//img/@src'
                ).get(),
                "department": card.xpath(
                    './/div[contains(@class, "person__department")]/text()'
                ).get(),
                "phone": card.xpath(
                    './/div[contains(@class, "person__location")]/text()'
                ).get(),
                "location": card.xpath(
                    './/div[contains(@class, "person__location")]/text()'
                ).get(),
                "email": card.xpath(
                    './/div[contains(@class, "person__email")]//a/text()'
                ).get(),
                "position": card.xpath(
                    './/div[contains(@class, "person__position")]/text()'
                ).get(),
            }
