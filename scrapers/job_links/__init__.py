from annotated_types import Gt
import typing

from models import JobLink


@typing.runtime_checkable
class LinkScrapingStrategy(typing.Protocol):
    __name__: str

    def __call__(
        self,
        *,
        batch_size: typing.Annotated[int, Gt(0)],
        n_links_to_collect: typing.Annotated[int, Gt(0)],
    ) -> typing.Generator[typing.List[JobLink], None, int]:
        """Every link crawler function has to be a Callable with
        these arguments and return type:
        ```python
            def example_crawler(
                batch_size: typing.Annotated[int, Gt(0)],
                n_links_to_collect: typing.Annotated[int, Gt(0)]
            ) -> typing.Generator[typing.List[str], None, int]:
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

        Returns
        -------
        int
            Total number of links collected (may be fewer than requested `n_links_to_collect`)

        Yields
        ------
        typing.List[str]
            `batch_size`-sized batches of links
        """

    ...
