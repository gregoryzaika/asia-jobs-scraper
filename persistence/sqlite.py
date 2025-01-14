from types import TracebackType
from annotated_types import Ge
import logging
import typing
import sqlite3
import pathlib

from persistence import JobDetailsRepository, JobLinkRepository
from models import JobDetails, JobLink, WebsiteIdentifier


class SqliteJobLinkRepository(JobLinkRepository):
    def __init__(self, db_file_location: pathlib.Path) -> None:
        self.connection = sqlite3.connect(db_file_location)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS job_links (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                link TEXT NOT NULL,
                website_identifier TEXT NOT NULL
            )
            """
        )

    def __enter__(self) -> "SqliteJobLinkRepository":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> typing.Literal[False]:
        self.connection.close()
        return False

    def save_batch(self, job_link_batch: typing.List[JobLink]) -> None:
        logging.info(f"Saving {len(job_link_batch)} job links")
        cursor = self.connection.cursor()
        result = cursor.executemany(
            "INSERT OR IGNORE INTO job_links VALUES(?, ?, ?, ?)",
            [
                (
                    job_link.id,
                    job_link.title,
                    job_link.link,
                    job_link.website_identifier.value,
                )
                for job_link in job_link_batch
            ],
        )
        self.connection.commit()
        logging.info(f"Saved {result.rowcount} new job links")

        cursor.close()

    def get_batch(
        self,
        website_identifier: WebsiteIdentifier,
        batch_size: typing.Annotated[int, Ge(0)],
        offset: typing.Annotated[int, Ge(0)],
    ) -> typing.List[JobLink]:
        cursor = self.connection.cursor()
        cursor.execute(
            """SELECT * FROM job_links
            WHERE website_identifier = ?
            LIMIT ? OFFSET ?""",
            (website_identifier.value, batch_size, offset),
        )
        rows = cursor.fetchall()
        cursor.close()

        return [JobLink(*row) for row in rows]

    def count(self, website_identifier: WebsiteIdentifier) -> int:
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM job_links WHERE website_identifier = ?",
            (website_identifier.value,),
        )
        count: int = cursor.fetchone()[0]
        cursor.close()
        return count


class SqliteJobDetailsRepository(JobDetailsRepository):
    def __init__(self, db_file_location: pathlib.Path) -> None:
        self.connection = sqlite3.connect(db_file_location)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS job_details (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT NOT NULL,
                salary_information TEXT,
                description TEXT NOT NULL,
                access_date TEXT NOT NULL,
                FOREIGN KEY (id) REFERENCES job_links(id)
            )
            """
        )

    def __enter__(self) -> "SqliteJobDetailsRepository":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> typing.Literal[False]:
        self.connection.close()
        return False

    def save_batch(self, job_details_batch: typing.List[JobDetails]) -> None:
        logging.info(f"Saving {len(job_details_batch)} job links")
        cursor = self.connection.cursor()
        result = cursor.executemany(
            """INSERT INTO job_details VALUES(?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
            title = excluded.title,
            company = excluded.company,
            location = excluded.location,
            salary_information = excluded.salary_information,
            description = excluded.description,
            access_date = excluded.access_date
            """,
            [
                (
                    job_details.id,
                    job_details.title,
                    job_details.company,
                    job_details.location,
                    job_details.salary_information,
                    job_details.description,
                    job_details.access_date,
                )
                for job_details in job_details_batch
            ],
        )
        self.connection.commit()
        logging.info(f"Saved {result.rowcount} new job links")

        cursor.close()
