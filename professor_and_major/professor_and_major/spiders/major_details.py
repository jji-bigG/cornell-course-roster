import scrapy
from bs4 import BeautifulSoup

import json


class MajorDetailsSpider(scrapy.Spider):
    name = "major_details"

    def start_requests(self):
        with open("links.json") as f:
            links = json.load(f)
        for link in links:
            yield scrapy.Request(url=link["link"], callback=self.parse)

    def parse(self, response):
        soup = BeautifulSoup(response.text, "lxml")

        # Set the text length threshold
        threshold = 100  # For example, minimum 100 characters

        # Define tags to exclude (e.g., headers, footers)
        exclude_tags = ["header", "footer", "nav", "script", "style"]

        # Find all tags and filter by text length and exclusion list
        for tag in soup.find_all():
            if tag.name in exclude_tags:
                continue

            text = tag.get_text(strip=True)
            if len(text) >= threshold:
                yield {
                    "url": response.url,
                    "tag": tag.name,
                    "text": text,
                }
