import scrapy


class CalsProfListSpider(scrapy.Spider):
    name = "cals_prof_list"
    allowed_domains = ["cals.cornell.edu"]
    start_urls = ["https://cals.cornell.edu/research/find-an-expert/all?page=0"]

    def parse(self, response):
        for prof in response.css("div.expert-card"):
            parsed_prof = {
                "name": prof.css("a.link::text").get(),
                "profile_url": response.urljoin(prof.css("a.link::attr(href)").get()),
                "image_url": response.urljoin(prof.css("img::attr(src)").get()),
                "title": prof.css("div.expert-content p.department::text").get(),
                "department": prof.css("div.title p.field__item::text").get(),
                "phone": prof.css(
                    "div.expert-card-back ul li a[href^='tel']::text"
                ).get(),
                "email": prof.css(
                    "div.expert-card-back ul li a[href^='mailto']::text"
                ).get(),
            }
            yield {
                "name": parsed_prof["name"].strip() if parsed_prof["name"] else None,
                "profile_url": (
                    parsed_prof["profile_url"].strip()
                    if parsed_prof["profile_url"]
                    else None
                ),
                "image_url": (
                    parsed_prof["image_url"].strip()
                    if parsed_prof["image_url"]
                    else None
                ),
                "title": parsed_prof["title"].strip() if parsed_prof["title"] else None,
                "department": (
                    parsed_prof["department"].strip()
                    if parsed_prof["department"]
                    else None
                ),
                "phone": parsed_prof["phone"].strip() if parsed_prof["phone"] else None,
                "email": parsed_prof["email"].strip() if parsed_prof["email"] else None,
            }

        next_page = response.css("a[rel='next']::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
