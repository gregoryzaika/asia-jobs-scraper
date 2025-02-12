import typing

import logging

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from models import JobLink, WebsiteIdentifier
from scrapers.job_links.strategies.selenium_strategy import SequentialSeleniumLinkCrawlingStrategy


WEBSITE_IDENTIFIER = WebsiteIdentifier.CAREERVIET


class CareervietSeleniumSequentialLinkCrawler(SequentialSeleniumLinkCrawlingStrategy):
    __name__ = "CareervietSeleniumSequentialLinkCrawler"

    def open_next_page(self, driver: webdriver.Remote, entrypoint_url: str) -> typing.Generator[None, None, None]:
        driver.get(entrypoint_url)
        yield

        while True:
            pagination_div: WebElement | None = driver.find_element(By.XPATH, '/html/body/main/section[2]/div/div/div[1]/div[2]/div[2]')
            next_page_button: WebElement | None = pagination_div.find_element(By.XPATH, '//li[contains(@class, "next-page")]/a')

            if next_page_button is None:
                logging.info("No `next-page` button")
                raise StopIteration
            else:
                next_page_button.click()
            yield

    def collect_links(
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
            '//*[@id="jobs-side-list-content"]//div[contains(@id, "job-item")]//div[contains(@class, "title")]//a[contains(@class, "job_link")]',
        )

        yield from (
            JobLink(
                str(job_link_element.get_attribute("data-id")),
                str(job_link_element.get_attribute("title")),
                str(job_link_element.get_attribute("href")),
                WEBSITE_IDENTIFIER,
            )
            for job_link_element in job_list_link_elements
            if all(
                job_link_element.get_attribute(attr) is not None
                for attr in ["data-id", "title", "href"]
            )
        )