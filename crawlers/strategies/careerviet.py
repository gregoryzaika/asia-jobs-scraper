import logging
import typing

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from crawlers.strategies.selenium_strategy import SequentialSeleniumLinkCrawlingStrategy
from models import JobLink, WebsiteIdentifier


class CareervietSeleniumSequentialLinkCrawler(SequentialSeleniumLinkCrawlingStrategy):
    __name__ = "CareervietSeleniumSequentialLinkCrawler"
    website = WebsiteIdentifier.CAREERVIET
    initial_page_url = "https://careerviet.vn/viec-lam/tat-ca-viec-lam-vi.html"

    def iterate_pages(
        self, driver: webdriver.Remote
    ) -> typing.Generator[None, None, None]:
        # open the first page
        driver.get(CareervietSeleniumSequentialLinkCrawler.initial_page_url)
        yield

        def get_next_page_button(driver: webdriver.Remote) -> WebElement | None:
            pagination_div: WebElement = driver.find_element(
                By.XPATH, "/html/body/main/section[2]/div/div/div[1]/div[2]/div[2]"
            )
            try:
                return pagination_div.find_element(
                    By.XPATH, '//li[contains(@class, "next-page")]/a'
                )
            except NoSuchElementException:
                logging.info("No next page button found. Exiting.")
                return None

        while (next_page_button := get_next_page_button(driver)) is not None:
            next_page_button.click()
            yield

    def iterate_links(
        self,
        driver: webdriver.Remote,
    ) -> typing.Generator[JobLink, None, None]:
        """Collects job links from the current page with
        job offers on the Careerviet website

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
            '//*[@id="jobs-side-list-content"]//div[contains(@id,'
            ' "job-item")]//div[contains(@class, "title")]//a[contains(@class,'
            ' "job_link")]',
        )

        for job_link_element in job_list_link_elements:
            data_id = job_link_element.get_attribute("data-id")
            title = job_link_element.get_attribute("title")
            href = job_link_element.get_attribute("href")
            if None not in (data_id, title, href):
                yield JobLink(
                    str(data_id),
                    str(title),
                    str(href),
                    CareervietSeleniumSequentialLinkCrawler.website,
                )
