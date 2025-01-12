from annotated_types import Gt
import typing
import random
import logging

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


# the website's search allows picking up to 15 regions
SARAMIN_N_REGIONS_SEARCH_CAP = 15


def collect_saramin_job_offer_links(
    batch_size: typing.Annotated[int, Gt(0)] = 10,
    n_links_to_collect: typing.Annotated[int, Gt(0)] = 100,
) -> typing.Generator[typing.List[str], None, int]:
    """A crawler that collects links to job offers.
    - Website: `https://www.saramin.co.kr/`.
    - Last successful execution: `12.01.2025`

    This function is indended to follow the `LinkScrapingStrategy` protocol.
    See this module's `LinkScrapingStrategy` for the description of the parameters.
    """
    driver = webdriver.Firefox()

    entrypoint_url = "https://www.saramin.co.kr/zf_user/jobs/list/domestic"
    driver.get(entrypoint_url)

    region_list: typing.List[WebElement] = driver.find_element(
        By.XPATH,
        "/html/body/div[3]/div[1]/div/div[2]/form/fieldset/div/div[2]/div/div[1]/div[2]/div[1]/div[2]/div/ul[1]",
    ).find_elements(By.TAG_NAME, "li")

    regions_pick_buttons: typing.List[WebElement] = [
        r.find_element(By.TAG_NAME, "button") for r in region_list
    ]

    # click on 15 randomly chosen regions
    for region_pick_button in random.sample(
        regions_pick_buttons,
        min(len(regions_pick_buttons), SARAMIN_N_REGIONS_SEARCH_CAP),
    ):
        region_pick_button.click()

    # click the search button
    driver.find_element(By.XPATH, "//*[@id=\"search_btn\"]").click()


    job_offer_list: typing.List[WebElement] = driver.find_element(
        By.XPATH,
        "/html/body/div[3]/div[1]/div/div[4]/div/div[3]/section"
    ).find_elements(By.TAG_NAME, "li")

    logging.info(f"Counted {len(job_offer_list)} offers")

    # driver.close()

    yield []



# summary_section = driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div[3]/section[1]/div[1]/div[2]")
# detail_section = driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div[3]/section[1]/div[1]/div[3]")