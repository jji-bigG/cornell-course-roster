import scrapy


class CalsDegreesSpider(scrapy.Spider):
    name = "cals_studies_list"
    start_urls = ["https://cals.cornell.edu/education/degrees-programs"]

    def parse(self, response):
        self.logger.info("Parsing the main page for categories.")

        # Extract the categories list within the interests subtab
        categories_list = response.css(
            "div#views-view--interests-categories ul.category li button"
        )

        if not categories_list:
            self.logger.warning("No categories found!")

        for category in categories_list:
            category_name = category.css("::text").get()
            category_id = category.css("::attr(data-target)").get().strip("#")

            self.logger.info(f"Found category: {category_name} with ID: {category_id}")

            yield {
                "category_name": category_name,
                "category_id": category_id,
            }

            subcategory_url = response.urljoin(f"#{category_id}")
            request = scrapy.Request(subcategory_url, callback=self.parse_subcategory)
            request.meta["category_name"] = category_name
            request.meta["category_id"] = category_id
            yield request

    def parse_subcategory(self, response):
        category_name = response.meta["category_name"]
        category_id = response.meta["category_id"]

        self.logger.info(f"Parsing subcategory: {category_name} with ID: {category_id}")

        subcategories = response.css(f"div#{category_id} div[id*='-interests']")

        if not subcategories:
            self.logger.warning(f"No subcategories found for {category_name}")

        for subcategory in subcategories:
            subcategory_id = subcategory.css("::attr(id)").get()
            degree_cards = subcategory.css("div.degree-card-layout div.degree-card")

            if not degree_cards:
                self.logger.warning(
                    f"No degree cards found in subcategory {subcategory_id}"
                )

            for card in degree_cards:
                yield self.extract_degree_info(card, category_name, subcategory_id)

    def extract_degree_info(self, card, category_name, subcategory_id):
        title = card.css("a.link::text").get()
        url = card.css("a.link::attr(href)").get()
        description = card.css("div.degree-card-front > p::text").get()
        degree_type = card.css("p.study span.field__item::text").get()
        image_url = card.css("div.degree-card-back img::attr(src)").get()
        careers = card.css("div.card-back-content div.field__item ul li::text").getall()

        if not title:
            self.logger.warning(
                f"No title found for a card in subcategory {subcategory_id}"
            )

        return {
            "category_name": category_name,
            "subcategory_id": subcategory_id,
            "title": title,
            "url": url,
            "description": description,
            "degree_type": degree_type,
            "image_url": image_url,
            "careers": careers,
        }
