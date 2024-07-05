from typing import Iterable
import scrapy
import json


class CalsStudiesDetailsSpider(scrapy.Spider):
    name = "cals_studies_details"
    allowed_domains = ["cals.cornell.edu"]

    def start_requests(self) -> Iterable[scrapy.Request]:
        with open("cals-studies-list.jsonl") as f:
            for line in f:
                data = json.loads(line)
                if data["url"].startswith("https://cals.cornell.edu"):
                    yield scrapy.Request(
                        url=data["url"],
                        callback=self.parse,
                        meta={"data": data},
                    )

    def parse(self, response: scrapy.http.Response):
        data = response.meta["data"]
        data["content"] = response.css("div.field--name-body").get()
        yield data
