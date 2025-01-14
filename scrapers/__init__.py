import typing
import logging
from annotated_types import Ge

from models import JobDetails, JobLink
from scrapers.job_details import DetailsScrapingStrategy
from scrapers.job_links import LinkScrapingStrategy


class LinkScraper:
    strategy: LinkScrapingStrategy

    def __init__(
        self,
        *,
        strategy: LinkScrapingStrategy,
        batch_size: int = 10,
        n_links_to_collect: int = 100,
    ):
        self.strategy = strategy
        self.batch_size = batch_size
        self.n_links_to_collect = n_links_to_collect

    def scrape(
        self,
        *,
        batch_size: typing.Annotated[int, Ge(0)],
        n_links_to_collect: typing.Annotated[int, Ge(0)],
    ) -> typing.Generator[typing.List[JobLink], None, int]:
        logging.info(
            f"\n--- Scraping links ---\n"
            f"\n\tScraping {n_links_to_collect} links\n"
            f"\tin batches with batch size {batch_size}\n"
            f"\tusing strategy `{self.strategy.__name__}`\n"
        )

        batch_generator = self.strategy(
            batch_size=batch_size, n_links_to_collect=n_links_to_collect
        )

        while True:
            try:
                batch = next(batch_generator)
            except StopIteration as n_links_collected:
                logging.info(
                    f"Success! `{self.strategy.__name__}` collected {n_links_collected} links"
                )
                return int(n_links_collected.value)

            logging.info(f"\tCollected {len(batch)} links")
            yield batch


class DetailScraper:
    strategy: DetailsScrapingStrategy

    def __init__(self, *, strategy: DetailsScrapingStrategy):
        self.strategy = strategy

    def scrape(self, *, links: typing.List[JobLink]) -> typing.List[JobDetails]:
        logging.info(
            f"\n--- Scraping details ---\n"
            f"\n\tScraping job details for {len(links)} links"
        )

        return self.strategy(links=links)
