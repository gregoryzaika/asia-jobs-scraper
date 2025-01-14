# asia-jobs-scraper

## Usage

### Collect links to job offers

The links will be extracted and written to the database in batches
with size `BACTH_SIZE`. The maximim number of links to collect will
be `N_LINKS`.

```sh
poetry run scrape links N_LINKS BATCH_SIZE
```

### Extract the job details after having collected the links

The details will be written to the database in batches with size `BATCH_SIZE`.

```sh
poetry run scrape details extract_job_details BATCH_SIZE
```

The links and the details will be stored in the pluggable SQLite database,
stored in the file `jobs.db`
You can set the path to the database in the configuration file `config.toml`.

```toml
[persistence.sqlite]
db_file_location = "path/to/sqlite.db"
```

## `mypy` type checks

```sh
poetry run mypy --strict .
```

## Code formatting with `black`

```sh
poetry run black .
```
