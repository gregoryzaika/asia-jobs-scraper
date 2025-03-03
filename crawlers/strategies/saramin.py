import logging
import random
import typing

from selenium import webdriver
from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support import ui

from crawlers.strategies.selenium_strategy import SequentialSeleniumLinkCrawlingStrategy
from models import JobLink, WebsiteIdentifier


class SaraminSeleniumSequentialLinkCrawler(SequentialSeleniumLinkCrawlingStrategy):
    __name__ = "SaraminSeleniumSequentialLinkCrawler"
    website = WebsiteIdentifier.SARAMIN
    initial_page_url = "https://www.saramin.co.kr/zf_user/jobs/list/domestic"
    n_region_search_cap = 15  # the website's search allows picking up to 15 regions

    def iterate_pages(
        self, driver: webdriver.Remote
    ) -> typing.Generator[None, None, None]:
        self._open_first_page(driver)
        yield

        while True:
            page_box = driver.find_element(
                By.XPATH,
                "//*[@id='default_list_wrap']/div[contains(@class, 'PageBox')]",
            )
            current_page_number = int(
                page_box.find_element(
                    By.XPATH,
                    "//span[contains(@class, 'BtnType') and contains(@class,"
                    " 'active')]",
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
                    # click on the button that displays the next 10 pages and opens
                    # the first one of them
                    page_box.find_element(
                        By.XPATH,
                        "//button[contains(@class, 'BtnType') and contains(@class,"
                        " 'BtnNext')]",
                    ).click()
                    yield

                except NoSuchElementException:
                    logging.info("No btnNext found")
                    return None

    def _open_first_page(self, driver: webdriver.Remote) -> None:
        driver.get(SaraminSeleniumSequentialLinkCrawler.initial_page_url)

        regions_pick_buttons: typing.List[WebElement] = driver.find_elements(
            By.XPATH,
            "/html/body/div[3]/div[1]/div/div[2]/form/fieldset/div/div[2]/"
            "div/div[1]/div[2]/div[1]/div[2]/div/ul[1]/li/button",
        )

        # click on 15 randomly chosen regions
        for region_pick_button in random.sample(
            regions_pick_buttons,
            min(
                len(regions_pick_buttons),
                SaraminSeleniumSequentialLinkCrawler.n_region_search_cap,
            ),
        ):
            try:
                region_pick_button.click()
            except ElementNotInteractableException:
                region_pick_button = ui.WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(region_pick_button)
                )
                region_pick_button.click()

        # click the search button
        search_btn = driver.find_element(By.XPATH, '//*[@id="search_btn"]')

        logging.info("search_btn: %s", search_btn)
        search_btn.click()

    def iterate_links(
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

        logging.info("Found %i job links on the page", len(job_list_link_elements))

        for job_link_element in job_list_link_elements:
            id_ = job_link_element.get_attribute("id")
            title = job_link_element.get_attribute("title")
            href = job_link_element.get_attribute("href")
            if None not in (id_, title, href):
                yield JobLink(
                    str(id_),
                    str(title),
                    str(href),
                    SaraminSeleniumSequentialLinkCrawler.website,
                )
