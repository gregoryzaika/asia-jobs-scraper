from annotated_types import Gt
from typing import Generator, Iterable, Tuple, Protocol, runtime_checkable, Annotated

from models import JobLink


@runtime_checkable
class LinkCrawlingStrategy(Protocol):
    __name__: str

    def __call__(
        self,
        *,
        batch_size: Annotated[int, Gt(0)],
        n_links_to_collect: Annotated[int, Gt(0)],
    ) -> Generator[Iterable[JobLink], None, None]:
        """Every link crawler function has to be a Callable with
        these arguments and return type:
        ```python
            def example_crawler(
                batch_size: typing.Annotated[int, Gt(0)],
                n_links_to_collect: typing.Annotated[int, Gt(0)]
            ) -> typing.Generator[typing.Iterable[str], None, None]:
            ...
        ```
        If the crawler is a `Callable` class instance, than that class's
        __call__ will also have the `self` argument, like this function itself.

        Parameters
        ----------
        batch_size : int
            Number of links in one batch of links yielded this generator
        n_links_to_collect : int
            Total number of links to collect

        Yields
        ------
        typing.Iterable[str]
            `batch_size`-sized batches of links
        """

    ...