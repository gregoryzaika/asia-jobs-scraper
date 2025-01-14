import logging
import typing
from datetime import datetime, timezone

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


from models import JobDetails, JobLink, WebsiteIdentifier

WEBSITE_IDENTIFIER = WebsiteIdentifier.SARAMIN


def collect_saramin_job_details(
    links: typing.List[JobLink],
) -> typing.List[JobDetails]:
    """See the `DetailsScrapingStrategy` protocol
    definition to get the description of the arguments
    and the return type

    NOTE:
    This can be parallelized with
    ```python
        from joblib import Parallel, delayed
        results = Parallel(n_jobs=-1)(delayed(collect_job_details_from_single_link)(link) for link in links)
    ```
    but selenium thows an error when I'm opening a driver for the second time
    """
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    collected_details = []

    for link in links:
        details: JobDetails | None = collect_job_details_from_single_link(driver, link)
        if details is not None:
            collected_details.append(details)
        else:
            logging.warning(
                f"""Extracting job details from the link returned None.
                Perhaps the job has expired or the page has an unusual
                structure. (link: {link.link})
                """
            )

    driver.close()

    return collected_details


def collect_job_details_from_single_link(
    driver: webdriver.Remote, link: JobLink
) -> JobDetails | None:
    logging.info(f"Retrieving details for job {link.title} (id {link.id})")
    driver.get(link.link)

    id = link.id

    try:
        title = driver.find_element(
            By.XPATH, "/html/body/div[3]/div/div/div[3]/section[1]/div[1]/div[1]/div/h1"
        ).text
    except NoSuchElementException:
        # oftern, the lack of the title element
        # signals that the job has expired - the None
        # will tell to the calling function to skip this
        # link
        return None

    try:
        company = driver.find_element(
            By.XPATH,
            "/html/body/div[3]/div/div/div[3]/section[1]/div[1]/div[1]/div/div[1]/a[contains(@class, 'company')]",
        ).get_attribute("title")
    except NoSuchElementException:
        company = "unspecified"

    try:
        location = driver.find_element(
            By.XPATH,
            "/html/body/div[3]/div/div/div[3]/section[1]/div[1]/div[5]/div/address/span[1]/span",
        ).text
    except NoSuchElementException:
        location = "unspecified"

    try:
        location_div: WebElement = driver.find_element(By.XPATH, "//*[@id='map_0']")
        alt_location = f"""{location_div.get_attribute("data-address")}; lat {location_div.get_attribute("data-latitude")}; long {location_div.get_attribute("data-longitude")}"""
        location = f"{location} ({alt_location})"
    except NoSuchElementException:
        alt_location = ""

    try:
        salary_information = driver.find_element(
            By.XPATH,
            "/html/body/div[3]/div/div/div[3]/section[1]/div[1]/div[2]/div/div[1]/dl[1]/dd",
        ).text
    except NoSuchElementException:
        salary_information = "unspecified"

    # so far only this has been loading some post-specific content
    # but the result is raw and has a repeating header and footer
    # from the saramin website
    # tried to go ahead with driver.switch_to.frame("iframe_content_0"),
    # but no luck yet
    user_iframe_body: WebElement = driver.find_element(
        By.XPATH, "//*[@id='iframe_content_0']"
    ).find_element(By.XPATH, "/html/body")

    return JobDetails(
        id=id,
        title=title,
        company=str(company),
        location=location,
        salary_information=salary_information,
        description=user_iframe_body.text,
        access_date=datetime.now(timezone.utc).astimezone().isoformat(),
    )
