from types import TracebackType
from annotated_types import Ge
import logging
import typing
import sqlite3
import pathlib

import rich.text
import rich.themes

from persistence import JobDetailsRepository, JobLinkRepository
from models import JobDetails, JobLink, WebsiteIdentifier


class SqliteJobLinkRepository(JobLinkRepository):
    LINKS_TABLE_NAME = "job_links"

    def __init__(self, db_file_location: pathlib.Path) -> None:
        self.connection = sqlite3.connect(db_file_location)
        self.connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {SqliteJobLinkRepository.LINKS_TABLE_NAME} (
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
            f"INSERT OR IGNORE INTO {SqliteJobLinkRepository.LINKS_TABLE_NAME} VALUES(?, ?, ?, ?)",
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

        n_duplicates: int = len(job_link_batch) - result.rowcount

        logging.info(f"Saved {result.rowcount} new job links ({n_duplicates} duplicates)")

        cursor.close()

    def get_batch(
        self,
        website_identifier: WebsiteIdentifier,
        batch_size: typing.Annotated[int, Ge(0)],
        offset: typing.Annotated[int, Ge(0)],
    ) -> typing.List[JobLink]:
        cursor = self.connection.cursor()
        cursor.execute(
            f"""SELECT * FROM {SqliteJobLinkRepository.LINKS_TABLE_NAME}
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
            f"SELECT COUNT(*) FROM {SqliteJobLinkRepository.LINKS_TABLE_NAME} WHERE website_identifier = ?",
            (website_identifier.value,),
        )
        count: int = cursor.fetchone()[0]
        cursor.close()
        return count


class SqliteJobDetailsRepository(JobDetailsRepository):
    DETAILS_TABLE_NAME = "job_details"

    def __init__(self, db_file_location: pathlib.Path) -> None:
        self.connection = sqlite3.connect(db_file_location)
        self.connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {SqliteJobDetailsRepository.DETAILS_TABLE_NAME} (
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
            f"""INSERT INTO {SqliteJobDetailsRepository.DETAILS_TABLE_NAME} VALUES(?, ?, ?, ?, ?, ?, ?)
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

        n_duplicates: int = len(job_details_batch) - result.rowcount

        logging.info(f"Saved {result.rowcount} new job links ({n_duplicates} duplicates)")

        cursor.close()
