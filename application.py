import logging.config
import typing

import fire
import logging
import sqlite3

from config import ApplictionConfig

from scrapers import LinkScraper
from scrapers.link_sraping.saramin import collect_saramin_job_offer_links

logging.basicConfig(level=logging.INFO)

LINK_SCRAPERS = {
    "saramin": LinkScraper(
        strategy=collect_saramin_job_offer_links, batch_size=10, n_links_to_collect=20
    )
}


class Application:
    """The CLI tool that allows invoking the main job-scraping functionalities."""

    def __init__(self):
        self.config = ApplictionConfig.load()

        logging.info(f"Initialized the application with config {self.config}")

    def collect_links_to_job_offers(self) -> typing.Generator:  # TODO
        """Provided the website and the search strategy, search the
        website's job offer lists, and collect the links to the
        job description pages, recording the access timestamp.

        Parameters
        ----------

        """

        for _, link_scraper in LINK_SCRAPERS.items():
            with sqlite3.connect(
                self.config.persistence.sqlite.db_file_location
            ) as database:
                yield from link_scraper.scrape()

    def extract_job_details(self) -> typing.Any:  # TODO
        """Given the previously collected links, open each of them,
        and try to extract the job details.

        Parameters
        ----------

        """

        with sqlite3.connect(
            self.config.persistence.sqlite.db_file_location
        ) as database:
            logging.info(f"Successfully connected to the database {database}")


if __name__ == "__main__":
    fire.Fire(Application)
