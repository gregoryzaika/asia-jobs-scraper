from typing import (
    Annotated,
    Callable,
    ClassVar,
    Generator,
    Protocol,
    Tuple,
    runtime_checkable,
)

from annotated_types import Gt

from models import JobLink, WebsiteIdentifier


@runtime_checkable
class LinkCrawlingStrategy(Protocol):
    __name__: ClassVar[str]
    website: ClassVar[WebsiteIdentifier]

    def __call__(
        self,
        *,
        batch_size: Annotated[int, Gt(0)],
        n_links_to_read: Annotated[int, Gt(0)],
    ) -> Generator[Tuple[JobLink, ...], None, None]:
        """Every link crawler function has to be a Callable with
        these arguments and return type:
        ```python
            def example_crawler(
                batch_size: typing.Annotated[int, Gt(0)],
                n_links_to_read: typing.Annotated[int, Gt(0)]
            ) -> typing.Generator[typing.Tuple[str], None, None]:
            ...
        ```
        If the crawler is a `Callable` class instance, than that class's
        __call__ will also have the `self` argument, like this function itself.

        Parameters
        ----------
        batch_size : int
            Number of links in one batch of links yielded this generator
        n_links_to_read : int
            Total number of links to collect

        Yields
        ------
        typing.Tuple[str]
            `batch_size`-sized batches of links
        """


def link_crawling_strategy(website_: WebsiteIdentifier):
    """A decorator for function-like strategies"""

    def wrapper(
        f: Callable[
            [Annotated[int, Gt(0)], Annotated[int, Gt(0)]],
            Generator[Tuple[JobLink, ...], None, None],
        ],
    ):
        class _(LinkCrawlingStrategy):
            __name__: ClassVar[str] = f.__name__
            website: ClassVar[WebsiteIdentifier] = website_

            def __call__(
                self,
                *,
                batch_size: Annotated[int, Gt(0)],
                n_links_to_read: Annotated[int, Gt(0)],
            ) -> Generator[Tuple[JobLink, ...], None, None]:
                return f(batch_size, n_links_to_read)

        return _

    return wrapper
