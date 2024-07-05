import scrapy


class CornellProfessorsSpider(scrapy.Spider):
    name = "as_prof_list"
    allowed_domains = ["as.cornell.edu"]
    start_urls = ["https://as.cornell.edu/directory?page=0"]

    def parse(self, response):
        # Extract professor cards
        professor_cards = response.css("div.views-row")

        for card in professor_cards:
            name = card.css("h2.personCard__name a::text").get()
            link = card.css("h2.personCard__name a::attr(href)").get()
            title = card.css("p.personCard__title::text").get()
            departments = card.css("div.personCard__departments::text").get()
            image_url = card.css("figure.personCard__image img::attr(src)").get()

            # Clean the extracted data
            if departments:
                departments = departments.strip()

            yield {
                "name": name.strip() if name else None,
                "link": response.urljoin(link),
                "title": title.strip() if title else None,
                "departments": departments.strip() if departments else None,
                "image_url": image_url.strip() if image_url else None,
            }

        # Pagination
        next_page = response.css("li.pager__item--next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)
