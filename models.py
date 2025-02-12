import enum
import dataclasses


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
    location: str
    salary_information: str
    description: str
    access_date: str
