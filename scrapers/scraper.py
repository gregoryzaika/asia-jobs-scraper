import typing
import logging
from annotated_types import Ge

from models import JobDetails, JobLink, WebsiteIdentifier
from scrapers.strategies import DetailsScrapingStrategy


class DetailScraper:
    WEBSITE_IDENTIFIER: WebsiteIdentifier
    strategy: DetailsScrapingStrategy

    def __init__(self, *, strategy: DetailsScrapingStrategy):
        self.strategy = strategy

    def scrape(self, *, links: typing.List[JobLink]) -> typing.List[JobDetails]:
        logging.info(
            f"\n--- Scraping details ---\n"
            f"\n\tScraping job details for {len(links)} links"
        )

        return self.strategy(links=links)
