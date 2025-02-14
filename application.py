import logging.config
import logging
from typing import Generator, List
from itertools import count, takewhile

import fire
import fire.docstrings
from selenium.webdriver import Remote, Chrome, ChromeOptions, Firefox, FirefoxOptions
from selenium.webdriver.common.options import ArgOptions
from rich.logging import RichHandler

from config import ApplictionConfig

from crawlers.crawler import LinkCrawler
from crawlers.strategies.careerviet import CareervietSeleniumSequentialLinkCrawler
from crawlers.strategies.saramin import SaraminSeleniumSequentialLinkCrawler
from models import JobDetails, JobLink
from persistence.sqlite import SqliteJobDetailsRepository, SqliteJobLinkRepository
from scrapers.scraper import DetailScraper
from scrapers.strategies.saramin import collect_saramin_job_details


DRIVER: type[Remote] = Firefox
OPTS: ArgOptions = FirefoxOptions()
OPTS.add_argument("--headless")

CRAWLERS = [
    LinkCrawler(strategy=SaraminSeleniumSequentialLinkCrawler(DRIVER, OPTS)),
    LinkCrawler(strategy=CareervietSeleniumSequentialLinkCrawler(DRIVER, OPTS)),
]

SCRAPERS = [DetailScraper(strategy=collect_saramin_job_details)]


class Application:
    """The CLI tool that runs the scraping scripts

    Usage
    -----
    Collect links to job offers:
    poetry run scrape links N_LINKS BATCH_SIZE

    Extract job details:
    poetry run scrape details extract_job_details BATCH_SIZE

    """

    def __init__(self) -> None:
        self.config = ApplictionConfig.load()
        logging.basicConfig(
            level=self.config.log_level,
            format="%(name)s - %(levelname)s - %(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True)],
        )
        logging.info(f"Initialized the application with config {self.config}")

    def links(self, n_links: int, batch_size: int) -> None:
        """Provided the website and the search strategy, search the
        website's job offer lists, and collect the links to the
        job description pages, recording the access timestamp.

        Parameters
        ----------
        n_links : int
            Total number of job links to go through
        batch_size : int
            How many links to collect in one step

        """
        with SqliteJobLinkRepository(
            self.config.persistence.sqlite.db_file_location
        ) as link_repository:
            for crawler in CRAWLERS:
                logging.info(f"")
                for batch in crawler.crawl(
                    batch_size=batch_size, n_links_to_read=n_links
                ):
                    link_repository.save_batch(batch)

    def details(self, batch_size: int) -> None:
        """Given the previously collected links, open each of them,
        and try to extract the job details.

        Parameters
        ----------
        batch_size : int
            How many saved links to retrieve and scrape the details for at once

        """
        with SqliteJobLinkRepository(
            self.config.persistence.sqlite.db_file_location
        ) as link_repository, SqliteJobDetailsRepository(
            self.config.persistence.sqlite.db_file_location
        ) as details_repository:
            for scraper in SCRAPERS:
                logging.info(f"Starting scraper {scraper.strategy.__name__}")
                website_id = scraper.WEBSITE_IDENTIFIER
                link_batches: Generator[List[JobLink], None, None] = (
                    link_repository.get_batch(website_id, batch_size, offset)
                    for offset in count(0, batch_size)
                )
                for batch in takewhile(lambda b: len(b) > 0, link_batches):
                    detail_batch: List[JobDetails] = scraper.scrape(links=batch)
                    logging.info(f"Extracted {len(batch)} details for {website_id}")
                    details_repository.save_batch(detail_batch)


def run():
    fire.Fire(Application)
