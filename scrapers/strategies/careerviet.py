import enum
import logging
import logging.config
import re
from typing import Tuple, cast

import requests
from bs4 import BeautifulSoup
from lxml import etree, html
from returns.result import Failure, Result, Success, safe

from models import JobDetails, JobLink, WebsiteIdentifier
from scrapers import PageExpired
from scrapers.strategy import detail_scraping_strategy


@detail_scraping_strategy(WebsiteIdentifier.CAREERVIET)
def careerviet_selenium_sequential(
    links: Tuple[JobLink, ...],
) -> Tuple[JobDetails, ...]:
    def handle_errors(e: Exception, url: str) -> bool:
        if isinstance(e, PageExpired):
            logging.warning(f"{e}; skipping link {url}")
            return True
        elif isinstance(e, requests.ReadTimeout):
            logging.warning(f"{e}; skipping link {url}")
            return True
        raise e

    return tuple(
        cast(JobDetails, res.unwrap())
        for link in links
        if not (res := collect_details(link)).alt(lambda e: handle_errors(e, link.link))
    )


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like"
        " Gecko) Chrome/58.0.3029.110 Safari/537.3"
    )
}


class XPATHS(enum.Enum):
    TITLE = "/html/head/title"
    LOCATION = (
        "/html/body/main/section[2]/div/div/div[2]/div/div[1]/section/div[1]/div/"
        "div[1]/div/div/p/a"
    )
    ALT_LOCATION = (
        "/html/body/main/section[2]/div/div/div[2]/div/div[1]/section/div[5]/div"
    )
    ADDRESS = (
        "/html/body/main/section[2]/div/div/div[2]/div/div[1]/section/div[5]/div/span"
    )
    SALARY = (
        "/html/body/main/section[2]/div/div/div[2]/div/"
        "div[1]/section/div[1]/div/div[3]/div/ul/li[1]/p"
    )
    ALT_SALARY = (
        "/html/body/main/section[3]/div/div/div/div[1]/"
        "div[2]/div/div/table/tbody/tr[2]/td[2]/p/*"
    )
    DESCRIPTION = "/html/body/main/section[2]/div/div/div[2]/div/div[1]/section/div[3]"
    ALT_DESCRIPTION = "/html/body/main/section[3]/div/div/div/div[1]/div[4]/div[1]"
    PAGE_EXPIRED_BANNER = "//div[contains(@class, 'no-search')"


@safe
def collect_details(link: JobLink) -> Result[JobDetails, PageExpired]:
    logging.info(
        "Retrieving details for job %s (id: %s, link: %s)",
        link.title,
        link.id,
        link.link,
    )

    response = requests.get(link.link, headers=HEADERS, timeout=20)
    response.raise_for_status()  # Raises an error if the request failed

    if response.url == "https://careerviet.vn/error.html":
        return Failure(PageExpired(link.link))

    soup = BeautifulSoup(response.content, "html.parser")

    dom: etree._Element = etree.HTML(str(soup))

    match element_exists(dom, XPATHS.PAGE_EXPIRED_BANNER):
        case Success(True):
            return Failure(PageExpired(link.link))
        case Success(False):
            pass
        case Failure(e):
            return Failure(e)

    job_title, company = (
        get_element_text(dom, XPATHS.TITLE.value)
        .map(lambda title: (title.removeprefix("Tuyển dụng ").split(" tại ")))
        .map(
            lambda split_title: (
                split_title[0],
                re.split(
                    r" 20[0-9][0-9]", split_title[1].removesuffix(" - CareerViet.vn")
                )[0],
            )
        )
        .unwrap()
    )

    location = (
        get_element_text(dom, XPATHS.LOCATION)
        .map(lambda location: f"{location};")
        .value_or("")
        + get_element_text(dom, XPATHS.ALT_LOCATION)
        .map(lambda alt_location: f" {alt_location};")
        .value_or("")
        + get_element_text(dom, XPATHS.ADDRESS)
        .map(lambda address: f" {address};")
        .value_or("")
    )

    salary_information = (
        get_element_text(dom, XPATHS.SALARY)
        .lash(lambda _: get_element_text(dom, XPATHS.ALT_SALARY))
        .value_or(None)
    )
    description = (
        get_element_as_text(dom, XPATHS.DESCRIPTION)
        .lash(lambda _: get_element_as_text(dom, XPATHS.ALT_DESCRIPTION))
        .unwrap()
    )

    return Success(
        JobDetails(
            id=link.id,
            title=job_title,
            company=company,
            location=location,
            salary_information=salary_information,
            description=description,
        )
    )


@safe
def get_element_text(
    dom: etree._Element, xpath: str | XPATHS, display_name: str | None = None
) -> str:
    if isinstance(xpath, XPATHS):
        display_name = xpath.name
        xpath = xpath.value

    if (
        isinstance(els := dom.xpath(xpath), list)
        and len(els) > 0
        and isinstance(el := els[0], etree._Element)
    ):
        if (text := el.text) is None:
            text = str(html.HtmlElement(el[0]).text_content())
        else:
            text = text
    else:
        raise ValueError(
            f"Unexpected value: {str(els)}: Expected list[lxml.etree._Element] for"
            f" {display_name}"
        )

    return text


@safe
def get_element_as_text(
    dom: etree._Element, xpath: str | XPATHS, display_name: str | None = None
) -> str:
    if isinstance(xpath, XPATHS):
        display_name = xpath.name
        xpath = xpath.value

    if isinstance(els := dom.xpath(xpath), list) and isinstance(
        el := els[0], etree._Element
    ):
        text: str = etree.tounicode(el)
    else:
        raise ValueError(
            f"Unexpected value: {str(els)}: Expected list[lxml.etree._Element] for"
            f" {display_name}"
        )

    return text


@safe
def element_exists(dom, xpath: XPATHS) -> bool:
    if isinstance(els := dom.xpath(xpath.value), list):
        if len(els) > 0:
            return True
        else:
            return False
    else:
        raise ValueError(
            f"Unexpected value: {str(els)}: Expected list[lxml.etree._Element] for"
            f" {xpath.name}"
        )
