# class="cu-table cu-table-minors"
import scrapy


class MajorsSpider(scrapy.Spider):
    name = "minors"
    start_urls = [
        "https://www.cornell.edu/academics/fields.cfm"
    ]  # Replace with the actual URL

    def parse(self, response):
        # Parse the table with class="cu-table cu-table-majors"
        rows = response.xpath('//table[@class="cu-table cu-table-minors"]/tbody/tr')
        for row in rows:
            major = row.xpath("td/a/text()").get()
            link = row.xpath("td/a/@href").get()
            yield {
                "major": major,
                "link": response.urljoin(link),  # Make sure the link is absolute
            }
