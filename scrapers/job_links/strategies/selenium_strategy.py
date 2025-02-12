
from annotated_types import Gt
from typing import Callable, Generator, Optional, Tuple, Protocol, runtime_checkable, Annotated
from itertools import batched, islice, product
import logging

from selenium import webdriver
from selenium.webdriver.common.options import BaseOptions

from models import JobLink
from scrapers.job_links.strategy import LinkCrawlingStrategy


@runtime_checkable
class SequentialSeleniumLinkCrawlingStrategy(LinkCrawlingStrategy, Protocol):
    __name__: str

    def __init__(self, init_driver_closure: Callable[[], webdriver.Remote], entrypoint_url: str):
        self.init_driver = init_driver_closure
        self.entrypoint_url = entrypoint_url

    def __call__(
        self,
        *,
        batch_size: Annotated[int, Gt(0)],
        n_links_to_collect: Annotated[int, Gt(0)],
    ) -> Generator[Tuple[JobLink], None, None]:
        with self.init_driver() as driver:
            links: Generator[JobLink, None, None] = (link for _, link in islice(
                product(self.open_next_page(driver, self.entrypoint_url), self.collect_links(driver)),
                n_links_to_collect
            ))
            batches: Generator[Tuple[JobLink], None, None] = batched(links, batch_size)

            for batch in batches:
                logging.info(f"Collected {len(batch)} job links")
                yield batch

    def open_next_page(self, driver: webdriver.Remote) -> Generator[None, None, None]:
        ...

    def collect_links(self, driver: webdriver.Remote) -> Generator[JobLink, None, None]:
        ...