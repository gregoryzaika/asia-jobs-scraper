import logging.config
import typing
from annotated_types import Ge

import fire
import logging

import fire.docstrings

from config import ApplictionConfig

from models import JobLink, WebsiteIdentifier
from persistence.sqlite import SqliteJobDetailsRepository, SqliteJobLinkRepository
from scrapers import DetailScraper, LinkCrawler
from scrapers.job_details.saramin import collect_saramin_job_details
from scrapers.job_links.strategies.careerviet import CareervietSeleniumSequentialLinkCrawler
from selenium import webdriver

from scrapers.job_links.strategies.saramin import SaraminSeleniumSequentialLinkCrawler

logging.basicConfig(level=logging.INFO)

SELENIUM_CHROME_OPTIONS = webdriver.ChromeOptions()
# SELENIUM_CHROME_OPTIONS.add_argument("--headless")

LINK_SCRAPERS = {
    # WebsiteIdentifier.SARAMIN: LinkCrawler(
    #     strategy=SaraminSeleniumSequentialLinkCrawler(
    #         lambda: webdriver.Chrome(options=SELENIUM_CHROME_OPTIONS),
    #         entrypoint_url="https://www.saramin.co.kr/zf_user/jobs/list/domestic",
    #     )
    # ),
    WebsiteIdentifier.CAREERVIET: LinkCrawler(
        strategy=CareervietSeleniumSequentialLinkCrawler(
            lambda: webdriver.Chrome(options=SELENIUM_CHROME_OPTIONS),
            entrypoint_url="https://careerviet.vn/viec-lam/tat-ca-viec-lam-vi.html",
        )
    ),
}

DETAIL_SCRAPERS = {
    WebsiteIdentifier.SARAMIN: DetailScraper(strategy=collect_saramin_job_details)
}

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
        logging.info(f"Initialized the application with config {self.config}")

    def links(self, n_links: int, batch_size: int) -> None:
        """Provided the website and the search strategy, search the
        website's job offer lists, and collect the links to the
        job description pages, recording the access timestamp.

        Parameters
        ----------

        """
        with SqliteJobLinkRepository(
            self.config.persistence.sqlite.db_file_location
        ) as link_repository:
            for _, link_scraper in LINK_SCRAPERS.items():
                link_batches_generator = link_scraper.scrape(
                    batch_size=batch_size, n_links_to_collect=n_links
                )

                while True:
                    try:
                        batch: typing.Iterable[JobLink] = next(link_batches_generator)
                        link_repository.save_batch(batch)
                    except StopIteration:
                        break

    def details(self, batch_size: int) -> None:
        """Given the previously collected links, open each of them,
        and try to extract the job details.

        Parameters
        ----------

        """
        with SqliteJobLinkRepository(
            self.config.persistence.sqlite.db_file_location
        ) as link_repository, SqliteJobDetailsRepository(
            self.config.persistence.sqlite.db_file_location
        ) as details_repository:
            for website_identifier, detail_scraper in DETAIL_SCRAPERS.items():
                logging.info(
                    f"Extracting job details for website `{website_identifier}`"
                )
                n_links_stored = link_repository.count(website_identifier)
                for batch_offset in range(0, n_links_stored, batch_size):
                    links = link_repository.get_batch(
                        website_identifier, batch_size, batch_offset
                    )
                    detail_batch = detail_scraper.scrape(links=links)
                    logging.info(f"Extracted job details from {len(links)} links")
                    details_repository.save_batch(detail_batch)


def run():
    fire.Fire(Application)
