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

WEBSITE_IDENTIFIER = WebsiteIdentifier.SARAMIN


# the website's search allows picking up to 15 regions
SARAMIN_N_REGIONS_SEARCH_CAP = 15


def collect_saramin_job_offer_links(
    batch_size: typing.Annotated[int, Gt(0)] = 10,
    n_links_to_collect: typing.Annotated[int, Gt(0)] = 100,
) -> typing.Generator[typing.List[JobLink], None, int]:
    """A crawler that collects links to job offers.
    - Website: `https://www.saramin.co.kr/`.
    - Last successful execution: `13.01.2025`

    This function is indended to follow the `LinkScrapingStrategy` protocol.
    See this module's `LinkScrapingStrategy` for the description of the parameters.
    """
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    entrypoint_url = "https://www.saramin.co.kr/zf_user/jobs/list/domestic"
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

    jobs_generator: typing.Generator[JobLink, None, None] = collect_jobs_from_jobs_page(
        driver
    )

    total_n_of_batches = ceil(n_links_to_collect / batch_size)
    links_left_to_collect = n_links_to_collect

    for i in range(total_n_of_batches):
        batch: typing.List[JobLink] = []

        # call next on the generator until the batch is full
        while len(batch) < min(batch_size, links_left_to_collect):
            try:
                batch.append(next(jobs_generator))
            except StopIteration:  # if no more jobs on the page
                # try opening the next page (returns None if no pages left)
                next_page_number: int | None = open_next_page(driver)

                # if there is a next page
                if isinstance(next_page_number, int):
                    logging.info(f"Opened page {next_page_number}")
                    # reset the jobs generator with the jobs from the next page
                    jobs_generator = collect_jobs_from_jobs_page(driver)

                # quit otherwise
                elif next_page_number is None:
                    logging.info("No more pages left to scrape")
                    break

        links_left_to_collect -= len(batch)
        yield batch

    driver.close()

    return n_links_to_collect - links_left_to_collect


def open_next_page(driver: webdriver.Remote) -> int | None:
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

    except NoSuchElementException:
        try:
            logging.info("Opening the next 10 pages")
            # click on the button that displays the next
            # 10 pages and opens the first one of them
            page_box.find_element(
                By.XPATH,
                "//button[contains(@class, 'BtnType') and contains(@class, 'BtnNext')]",
            ).click()

        except NoSuchElementException:
            logging.info("No btnNext found")
            return None

    return current_page_number + 1


def collect_jobs_from_jobs_page(
    driver: webdriver.Remote,
) -> typing.Generator[JobLink, None, None]:
    """Collects job links from the current page with
    job offers on the Saramin website

    Parameters
    ----------
    driver : webdriver.Firefox
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
        if all_job_link_attrs_present(job_link_element)
    )


def all_job_link_attrs_present(job_link_element: WebElement) -> bool:
    for attr in ["id", "title", "href"]:
        if job_link_element.get_attribute(attr) is None:
            logging.info(f"Job link element missing {attr}. Skipping.")
            return False
    return True
