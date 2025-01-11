from string import digits
import typing

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

class SaraminRegionElement:
    def __init__(self, name: str, element: WebElement, offer_count):
        self.name = name
        self.element = WebElement
        self.offer_count = offer_count

def crawl_saramin():
    driver = webdriver.Firefox()

    entrypoint_url = "https://www.saramin.co.kr/zf_user/jobs/list/domestic"
    driver.get(entrypoint_url)

    # locate the <ul> with the regions
    # get all `region (offer count)` elements
    regions: typing.List[WebElement] = (driver
        .find_element(By.XPATH, "/html/body/div[3]/div[1]/div/div[2]/form/fieldset/div/div[2]/div/div[1]/div[2]/div[1]/div[2]/div/ul[1]")
        .find_elements(By.TAG_NAME, "li")
    )

    regions_pick_buttons: typing.Generator[WebElement] = (r.find_element(By.TAG_NAME, "button") for r in regions)

    offer_count_by_region: typing.Dict[] = {
        b.find_element(By.CLASS_NAME, "txt").text:
            int(''.join(d for d in b.find_element(By.CLASS_NAME, "count").text if d in digits))
        for b in regions_pick_buttons
        if not (
            len(b.find_element(By.CLASS_NAME, "txt").text) == 0
            or
            len(b.find_element(By.CLASS_NAME, "count").text) == 0
        )
    }

    print(offer_count_by_region)


websites = {
    "saramin": {
        "strategy": crawl_saramin,
    }
}
