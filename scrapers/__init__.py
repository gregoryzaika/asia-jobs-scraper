import logging


class PageExpired(Exception):
    def __init__(self, url: str):
        self.url = str

    def __str__(self):
        return f"The page at {self.url} is no longer available."

    def log(
        self,
        extra_info: str = "",
        level: int = logging.WARNING,
    ) -> bool:
        msg = f"{self}. {extra_info}"
        logging.log(level=level, msg=msg)
        return True
