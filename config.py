import pathlib
import sys
from typing import Literal

import pydantic

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


DEFAULT_CONFIG_LOCATION = pathlib.Path("config.toml")


class ApplictionConfig(pydantic.BaseModel):
    """Contains configuration values for this application.
    One of the ways to set them is in the `config.toml` file.
    """

    persistence: "Persistence"
    log_level: (
        Literal["INFO"] | Literal["WARNING"] | Literal["DEBUG"] | Literal["ERROR"]
    )

    class Persistence(pydantic.BaseModel):
        """Persistence-related/database configuration"""

        sqlite: "Sqlite"

        class Sqlite(pydantic.BaseModel):
            """The application's persistence is running on SQLite:
            all configuration related to it should go here.
            """

            db_file_location: pathlib.Path

    @classmethod
    def load(
        cls, config_path: pathlib.Path = DEFAULT_CONFIG_LOCATION
    ) -> "ApplictionConfig":
        """Read configuration from the file pointed by the
        `DEFAULT_CONFIG_LOCATION` variable
        """
        with open(config_path, "rb") as config_file:
            config = tomllib.load(config_file)
            return ApplictionConfig(**config)
