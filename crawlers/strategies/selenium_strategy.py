from annotated_types import Gt
from typing import (
    Generator,
    List,
    Tuple,
    Protocol,
    runtime_checkable,
    Annotated,
    Callable
)
from itertools import batched, islice, product
import logging

from selenium import webdriver
from selenium.webdriver.common.options import BaseOptions

from models import JobLink
from crawlers.strategy import LinkCrawlingStrategy


@runtime_checkable
class SequentialSeleniumLinkCrawlingStrategy(LinkCrawlingStrategy, Protocol):
    """This subclass is a protocol for a strategy that uses a Selenium WebDriver,
    while crawling job links page by page.

    NOTE:
    For websites that have infinite scrolling, the strategy can be used, too,
    but the `iterate_pages` method should be scrollong to the bottom of the page,
    and the `iterate_links` method should remember where it left off, e.g. by storing
    the number of links it has already collected, and then collecting new links starting
    at that number + 1.
    """

    __name__: str
    init_driver: Callable

    def __init__(
        self,
        driver_type: type[webdriver.Remote],
        driver_options: BaseOptions | List[BaseOptions] | None,
    ):
        self.init_driver = lambda: driver_type(options=driver_options)

    def __call__(
        self,
        *,
        batch_size: Annotated[int, Gt(0)],
        n_links_to_read: Annotated[int, Gt(0)],
    ) -> Generator[Tuple[JobLink], None, None]:
        with self.init_driver() as driver:
            links: Generator[JobLink, None, None] = islice(
                (
                    link
                    for _ in self.iterate_pages(driver)
                    for link in self.iterate_links(driver)
                ),
                n_links_to_read,
            )

            for batch in batched(links, batch_size):
                logging.info(f"Collected {len(batch)} job links")
                yield batch

    def iterate_pages(
        self, driver: webdriver.Remote
    ) -> Generator[None, None, None]: ...

    def iterate_links(
        self, driver: webdriver.Remote
    ) -> Generator[JobLink, None, None]: ...
