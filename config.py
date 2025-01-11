import pathlib
import pydantic
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


DEFAULT_CONFIG_LOCATION = pathlib.Path("config.toml")


class ApplictionConfig(pydantic.BaseModel):
    persistence: "Persistence"

    class Persistence(pydantic.BaseModel):
        sqlite: "Sqlite"

        class Sqlite(pydantic.BaseModel):
            db_file_location: pathlib.Path

    @classmethod
    def load(
        cls, config_path: pathlib.Path = DEFAULT_CONFIG_LOCATION
    ) -> "ApplictionConfig":
        with open(config_path, "rb") as config_file:
            config = tomllib.load(config_file)
            return ApplictionConfig(**config)
