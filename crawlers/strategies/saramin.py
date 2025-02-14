from annotated_types import Gt
from math import ceil
import typing
import random
import logging

from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

from crawlers.strategies.selenium_strategy import SequentialSeleniumLinkCrawlingStrategy
from models import JobLink, WebsiteIdentifier


class SaraminSeleniumSequentialLinkCrawler(SequentialSeleniumLinkCrawlingStrategy):
    __name__ = "SaraminSeleniumSequentialLinkCrawler"
    WEBSITE_IDENTIFIER = WebsiteIdentifier.SARAMIN
    INITIAL_PAGE_URL = "https://www.saramin.co.kr/zf_user/jobs/list/domestic"
    # the website's search allows picking up to 15 regions
    SARAMIN_N_REGIONS_SEARCH_CAP = 15

    def iterate_pages(
        self, driver: webdriver.Remote
    ) -> typing.Generator[None, None, None]:
        self._open_first_page(driver)
        yield

        while True:
            page_box = driver.find_element(
                By.XPATH,
                f"//*[@id='default_list_wrap']/div[contains(@class, 'PageBox')]",
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

    def _open_first_page(self, driver: webdriver.Remote) -> None:
        driver.get(SaraminSeleniumSequentialLinkCrawler.INITIAL_PAGE_URL)

        regions_pick_buttons: typing.List[WebElement] = driver.find_elements(
            By.XPATH,
            "/html/body/div[3]/div[1]/div/div[2]/form/fieldset/div/div[2]/div/div[1]/div[2]/div[1]/div[2]/div/ul[1]/li/button",
        )

        # click on 15 randomly chosen regions
        for region_pick_button in random.sample(
            regions_pick_buttons,
            min(
                len(regions_pick_buttons),
                SaraminSeleniumSequentialLinkCrawler.SARAMIN_N_REGIONS_SEARCH_CAP,
            ),
        ):
            try:
                region_pick_button.click()
            except ElementNotInteractableException as e:
                region_pick_button = ui.WebDriverWait(driver, 10).until(EC.element_to_be_clickable(region_pick_button))
                region_pick_button.click()

        # click the search button
        search_btn = driver.find_element(By.XPATH, '//*[@id="search_btn"]')

        logging.info(f"search_btn: {search_btn}")
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

        logging.info(f"Found {len(job_list_link_elements)} job links on the page")

        for job_link_element in job_list_link_elements:
            id_ = job_link_element.get_attribute("id")
            title = job_link_element.get_attribute("title")
            href = job_link_element.get_attribute("href")
            if None not in (id_, title, href):
                yield JobLink(
                    str(id_),
                    str(title),
                    str(href),
                    SaraminSeleniumSequentialLinkCrawler.WEBSITE_IDENTIFIER,
                )
