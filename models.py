import dataclasses
import enum
from datetime import datetime, timezone
from typing import Optional


class WebsiteIdentifier(enum.Enum):
    SARAMIN = "saramin"
    CAREERVIET = "careerviet"


@dataclasses.dataclass
class JobLink:
    id: str
    title: str
    link: str
    website_identifier: WebsiteIdentifier


@dataclasses.dataclass
class JobDetails:
    id: str
    title: str
    company: str
    location: Optional[str]
    salary_information: Optional[str]
    description: str
    access_date: str = dataclasses.field(
        default_factory=lambda: datetime.now(timezone.utc).astimezone().isoformat()
    )
