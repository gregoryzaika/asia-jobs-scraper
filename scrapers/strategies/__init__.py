from typing import List, Protocol, runtime_checkable

from models import JobDetails, JobLink


@runtime_checkable
class DetailsScrapingStrategy(Protocol):
    __name__: str

    def __call__(self, *, links: List[JobLink], **kwargs) -> List[JobDetails]:
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
