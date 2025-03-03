from typing import Callable, ClassVar, Protocol, Tuple, runtime_checkable

from models import JobDetails, JobLink, WebsiteIdentifier


@runtime_checkable
class DetailScrapingStrategy(Protocol):
    __name__: ClassVar[str]
    website: ClassVar[WebsiteIdentifier]

    def __call__(self, *, links: Tuple[JobLink, ...]) -> Tuple[JobDetails, ...]:
        """Given a list of job links, collect the job details

        Parameters
        ----------
        links : typing.List[JobLink]
            All job links from which to collect job details

        Returns
        ------
        typing.List[str]
            A list of job details
        """

    ...


def detail_scraping_strategy(website_: WebsiteIdentifier):
    """A decorator for function-like strategies"""

    def wrapper(f: Callable[[Tuple[JobLink, ...]], Tuple[JobDetails, ...]]):
        class _(DetailScrapingStrategy):
            __name__: ClassVar[str] = f.__name__
            website: ClassVar[WebsiteIdentifier] = website_

            def __call__(self, *, links: Tuple[JobLink, ...]) -> Tuple[JobDetails, ...]:
                return f(links)

        return _()

    return wrapper
