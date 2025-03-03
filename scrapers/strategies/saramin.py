import logging
import typing

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Remote
from selenium.webdriver.common.by import By
from selenium.webdriver.common.options import ArgOptions
from selenium.webdriver.remote.webelement import WebElement

from models import JobDetails, JobLink, WebsiteIdentifier
from scrapers.strategy import DetailScrapingStrategy, detail_scraping_strategy


def init_saramin_selenium_scraper(
    driver_type: type[Remote], driver_options: ArgOptions
) -> DetailScrapingStrategy:
    """
    Parameters
    ----------
    driver_type : type[Remote]
        The type of the Selenium driver (Firefox, Chrome, etc.)
    driver_options : BaseOptions
        The options that are compatible with the driver
    """

    @detail_scraping_strategy(WebsiteIdentifier.SARAMIN)
    def saramin_selenium_sequential(
        links: typing.Tuple[JobLink, ...],
    ) -> typing.Tuple[JobDetails, ...]:
        """
        Parameters
        ---------
        links : Tuple[JobLink, ...])
            The job links saved earlier retreived from the repository

        See the `DetailsScrapingStrategy` protocol
        definition to get the description of the arguments
        and the return type

        NOTE:
        This could be parallelized with `joblib.Parallel` and `joblib.delayed`, but
        Selenium raises an error when I'm creating a driver for the second time and
        then close the first instance.
        """
        with driver_type(options=driver_options) as driver:
            return tuple(
                details
                for link in links
                if (details := collect_details(driver, link)) is not None
            )

    return saramin_selenium_sequential


def collect_details(driver: Remote, link: JobLink) -> JobDetails | None:
    logging.info(f"Retrieving details for job {link.title} (id {link.id})")
    driver.get(link.link)

    id = link.id

    try:
        title = driver.find_element(
            By.XPATH, "/html/body/div[3]/div/div/div[3]/section[1]/div[1]/div[1]/div/h1"
        ).text
    except NoSuchElementException as e:
        logging.warning(f"""The job details page was missing an element.
                Perhaps the job has expired or the page has an unusual
                structure. (link: {link}, error: {e})
            """)
        return None

    try:
        company = driver.find_element(
            By.XPATH,
            "/html/body/div[3]/div/div/div[3]/section[1]/div[1]/div[1]/div/div[1]/"
            "a[contains(@class, 'company')]",
        ).get_attribute("title")
    except NoSuchElementException:
        company = None

    try:
        location = driver.find_element(
            By.XPATH,
            "/html/body/div[3]/div/div/div[3]/section[1]/div[1]/"
            "div[5]/div/address/span[1]/span",
        ).text
    except NoSuchElementException:
        location = None

    try:
        location_div: WebElement = driver.find_element(By.XPATH, "//*[@id='map_0']")
        alt_location = (
            f"{location_div.get_attribute('data-address')}; "
            f"lat {location_div.get_attribute('data-latitude')}; "
            f"long {location_div.get_attribute('data-longitude')}"
        )
        location = f"{location} ({alt_location})"
    except NoSuchElementException:
        alt_location = ""

    try:
        salary_information = driver.find_element(
            By.XPATH,
            "/html/body/div[3]/div/div/div[3]/section[1]/"
            "div[1]/div[2]/div/div[1]/dl[1]/dd",
        ).text
    except NoSuchElementException:
        salary_information = None

    try:
        # so far only this has been loading some post-specific content
        # but the result is raw and has a repeating header and footer
        # from the saramin website
        # tried to go ahead with driver.switch_to.frame("iframe_content_0"),
        # but no luck yet
        user_iframe_body: WebElement = driver.find_element(
            By.XPATH, "//*[@id='iframe_content_0']"
        ).find_element(By.XPATH, "/html/body")
        description = user_iframe_body.text
    except NoSuchElementException:
        description = ""

    return JobDetails(
        id=id,
        title=title,
        company=str(company),
        location=location,
        salary_information=salary_information,
        description=description,
    )
