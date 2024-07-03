import scrapy
from bs4 import BeautifulSoup


class TextLengthSpider(scrapy.Spider):
    name = "text_length_spider"
    start_urls = [
        "https://dyson.cornell.edu/programs/undergraduate/academics/degree-requirements/"
    ]  # Add your target URLs here

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
                yield {"url": response.url, "tag": tag.name, "text": text}
