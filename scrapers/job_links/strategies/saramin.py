from annotated_types import Gt
from math import ceil
import typing
import random
import logging

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from models import JobLink, WebsiteIdentifier
from scrapers.job_links.strategies.selenium_strategy import SequentialSeleniumLinkCrawlingStrategy

WEBSITE_IDENTIFIER = WebsiteIdentifier.SARAMIN

# the website's search allows picking up to 15 regions
SARAMIN_N_REGIONS_SEARCH_CAP = 15

class SaraminSeleniumSequentialLinkCrawler(SequentialSeleniumLinkCrawlingStrategy):
    __name__ = "SaraminSeleniumSequentialLinkCrawler"

    def open_next_page(self, driver: webdriver.Remote, entrypoint_url: str) -> typing.Generator[None, None, None]:
        yield self._open_first_page(driver, entrypoint_url) # open the first page - different from the rest
        while True:
            page_box = driver.find_element(
                By.XPATH, f"//*[@id='default_list_wrap']/div[contains(@class, 'PageBox')]"
            )
            current_page_number = int(
                page_box.find_element(
                    By.XPATH,
                    "//span[contains(@class, 'BtnType') and contains(@class, 'active')]",
                ).text
            )

            try:
                # click on the next page button
                page_box.find_element(
                    By.XPATH, f"//button[number(@page) = {current_page_number + 1}]"
                ).click()
                yield

            except NoSuchElementException:
                try:
                    logging.info("Opening the next 10 pages")
                    # click on the button that displays the next 10 pages and opens the first one of them
                    page_box.find_element(
                        By.XPATH,
                        "//button[contains(@class, 'BtnType') and contains(@class, 'BtnNext')]",
                    ).click()
                    yield

                except NoSuchElementException:
                    logging.info("No btnNext found")
                    return None


    def _open_first_page(self, driver: webdriver.Remote, entrypoint_url: str) -> None:
        driver.get(entrypoint_url)

        regions_pick_buttons: typing.List[WebElement] = driver.find_elements(
            By.XPATH,
            "/html/body/div[3]/div[1]/div/div[2]/form/fieldset/div/div[2]/div/div[1]/div[2]/div[1]/div[2]/div/ul[1]/li/button",
        )

        # click on 15 randomly chosen regions
        for region_pick_button in random.sample(
            regions_pick_buttons,
            min(len(regions_pick_buttons), SARAMIN_N_REGIONS_SEARCH_CAP),
        ):
            region_pick_button.click()

        # click the search button
        driver.find_element(By.XPATH, '//*[@id="search_btn"]').click()


    def collect_links(
        self,
        driver: webdriver.Remote,
    ) -> typing.Generator[JobLink, None, None]:
        """Collects job links from the current page with
        job offers on the Saramin website

        Parameters
        ----------
        driver : webdriver.Remote
            The driver from the caller function

        Yields
        ------
        JobLink
            The next job link found on the page
        """
        job_list_link_elements: typing.List[WebElement] = driver.find_elements(
            By.XPATH,
            "//*[@id='default_list_wrap']/section//*[starts-with(@id, 'rec_link_')]",
        )

        logging.info(f"Found {len(job_list_link_elements)} job links on the page")

        yield from (
            JobLink(
                str(job_link_element.get_attribute("id")),
                str(job_link_element.get_attribute("title")),
                str(job_link_element.get_attribute("href")),
                WEBSITE_IDENTIFIER,
            )
            for job_link_element in job_list_link_elements
            if self._all_job_link_attrs_present(job_link_element)
        )

    @staticmethod
    def _all_job_link_attrs_present(job_link_element: WebElement) -> bool:
        for attr in ["id", "title", "href"]:
            if job_link_element.get_attribute(attr) is None:
                logging.info(f"Job link element missing {attr}. Skipping.")
                return False
        return True
