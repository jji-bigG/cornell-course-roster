import scrapy


class CalsStudiesListSpider(scrapy.Spider):
    name = "cals_studies_list"
    start_urls = ["https://cals.cornell.edu/education/degrees-programs"]

    def parse(self, response):
        # Find all panels
        panels = response.css(
            "div.field--name-field-program-items .panel.panel-default"
        )

        for panel in panels:
            # Extract the category name
            category = panel.css("div.panel-heading::text").get().strip()

            # Process each subcategory: undergraduate, graduate, non-degree
            subcategories = ["undergraduate", "graduate", "non-degree"]
            for subcategory in subcategories:
                subcategory_id = f"{category.lower().replace(' ', '-')}-{subcategory}-programs-interests"

                # Find all degree cards in this subcategory
                degree_cards = panel.css(f"div#{subcategory_id} div.degree-card")

                for card in degree_cards:
                    item = {
                        "category": category,
                        "subcategory": subcategory,
                        "title": card.css("div.degree-card-front a.link::text").get(),
                        "description": card.css("div.degree-card-front p::text").get(),
                        "url": response.urljoin(
                            card.css("div.degree-card-front a.link::attr(href)").get()
                        ),
                        "type": card.css(
                            "div.degree-card-front p.study span.field__item::text"
                        ).get(),
                    }
                    yield {
                        "category": (
                            item["category"].strip() if item["category"] else None
                        ),
                        "subcategory": (
                            item["subcategory"].strip() if item["subcategory"] else None
                        ),
                        "title": item["title"].strip() if item["title"] else None,
                        "description": (
                            item["description"].strip() if item["description"] else None
                        ),
                        "url": item["url"].strip() if item["url"] else None,
                        "type": item["type"].strip() if item["type"] else None,
                    }
