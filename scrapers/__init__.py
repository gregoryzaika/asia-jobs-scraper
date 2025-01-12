import typing
import logging

from scrapers.link_sraping import LinkScrapingStrategy


class LinkScraper:
    strategy: LinkScrapingStrategy
    batch_size: int
    n_links_to_collect: int

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

    def scrape(self):
        logging.info(f"Starting link crawler {self.__class__.__name__}:")

        try:
            yield from self.strategy(self.batch_size, self.n_links_to_collect)
        except StopIteration as result:
            logging.info(
                f"Link crawler {self.__class__.__name__} succeeded with result {result}:"
            )
