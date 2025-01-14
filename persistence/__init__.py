import typing
from annotated_types import Ge

from models import JobDetails, JobLink, WebsiteIdentifier


class JobLinkRepository(typing.Protocol):
    def save_batch(self, job_link_batch: typing.List[JobLink]) -> None: ...
    def get_batch(
        self,
        website_identifier: WebsiteIdentifier,
        batch_size: typing.Annotated[int, Ge(0)],
        offset: typing.Annotated[int, Ge(0)],
    ) -> typing.List[JobLink]: ...
    def count(self, website_identifier: WebsiteIdentifier) -> int: ...


class JobDetailsRepository(typing.Protocol):
    def save_batch(self, job_details_batch: typing.List[JobDetails]) -> None: ...
