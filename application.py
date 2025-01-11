import logging.config
import typing

import fire
import logging
import sqlite3

from config import ApplictionConfig
from crawlers import websites

# TODO: setup logging
logging.basicConfig(level=logging.DEBUG)

class Application:
    """The CLI tool that allows invoking the main job-scraping functionalities."""

    def collect_links_to_job_offers(self) -> typing.Generator:  # TODO
        """Provided the website and the search strategy, search the
        website's job offer lists, and collect the links to the
        job description pages, recording the access timestamp.

        Parameters
        ----------

        """

        for (website_name, website_meta) in websites.items():
            print(f"Crawling {website_name}")
            website_meta['strategy']()

        # raise NotImplementedError()

    def extract_job_details(self) -> typing.Any:  # TODO
        """Given the previously collected links, open each of them,
        and try to extract the job details.

        Parameters
        ----------

        """
        config = ApplictionConfig.load()

        logging.info("Initialized application config")
        logging.debug(config)

        with sqlite3.connect(config.persistence.sqlite.db_file_location) as database:
            logging.info(f"Successfully connected to the database {database}")


if __name__ == "__main__":
    fire.Fire(Application)


