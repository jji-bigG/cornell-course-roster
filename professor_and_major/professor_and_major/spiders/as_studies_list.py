# https://as.cornell.edu/majors-and-minors
import scrapy


class AsMajorsListSpider(scrapy.Spider):
    name = "as_majors_list"
    allowed_domains = ["as.cornell.edu"]
    start_urls = ["https://as.cornell.edu/majors-and-minors"]

    def parse(self, response):
        cards = response.css("div.views-row")

        for card in cards:
            title = card.css("h2.card__title a::text").get().strip()
            url = card.css("h2.card__title a::attr(href)").get()
            levels = list(set(card.css("div.levels span.level::text").getall()))
            image_url = card.css("figure img::attr(src)").get()
            description = card.css("div.teaser__copy p::text").get(default="").strip()

            yield {
                "title": title,
                "url": response.urljoin(url),
                "levels": levels,
                "image_url": image_url,
                "description": description,
            }
