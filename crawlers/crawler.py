import logging
import typing

from annotated_types import Ge

from crawlers.strategy import LinkCrawlingStrategy
from models import JobLink


class LinkCrawler:
    strategy: LinkCrawlingStrategy

    def __init__(
        self,
        *,
        strategy: LinkCrawlingStrategy,
        batch_size: int = 10,
        n_links_to_read: int = 100,
    ):
        self.strategy = strategy
        self.batch_size = batch_size
        self.n_links_to_read = n_links_to_read

    def crawl(
        self,
        *,
        batch_size: typing.Annotated[int, Ge(0)],
        n_links_to_read: typing.Annotated[int, Ge(0)],
    ) -> typing.Generator[typing.Tuple[JobLink, ...], None, int]:
        logging.info(
            "\n--- Scraping links ---\n"
            "\n\tScraping %i links\n"
            "\tin batches with batch size %i\n"
            "\tusing strategy `%s`\n",
            n_links_to_read,
            batch_size,
            self.strategy.__name__,
        )

        batch_generator = self.strategy(
            batch_size=batch_size, n_links_to_read=n_links_to_read
        )

        n_links_collected = 0
        for batch in batch_generator:
            yield batch
            n_links_collected += len(batch)

        logging.info(
            "Success! %s collected %i links", self.strategy.__name__, n_links_collected
        )

        return int(n_links_collected)
