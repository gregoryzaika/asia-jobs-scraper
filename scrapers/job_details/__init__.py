from annotated_types import Gt
import typing

from models import JobDetails, JobLink


@typing.runtime_checkable
class DetailsScrapingStrategy(typing.Protocol):
    __name__: str

    def __call__(self, *, links: typing.List[JobLink]) -> typing.List[JobDetails]:
        """Given a list of job links, collect the job details

        Parameters
        ----------
        links : typing.List[JobLink]
            All job links from which to collect job details

        Returns
        -------
        int
            Total number of job details collected

        Yields
        ------
        typing.List[str]
            `batch_size`-sized batches of links
        """

    ...
