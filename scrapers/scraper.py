import logging
import typing

from models import JobDetails, JobLink
from scrapers.strategy import DetailScrapingStrategy


class DetailScraper:
    strategy: DetailScrapingStrategy

    def __init__(self, *, strategy: DetailScrapingStrategy):
        self.strategy = strategy

    def scrape(
        self, *, links: typing.Tuple[JobLink, ...]
    ) -> typing.Tuple[JobDetails, ...]:
        logging.info(
            "\n--- Scraping details ---\n"
            f"\n\tScraping job details for {len(links)} links"
        )
        return self.strategy(links=links)
