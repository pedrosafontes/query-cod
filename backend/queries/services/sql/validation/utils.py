import re


def is_date_format(s: str) -> bool:
    return bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', s))


def is_time_format(s: str) -> bool:
    return bool(re.fullmatch(r'\d{2}:\d{2}(:\d{2})?', s))


def is_timestamp_format(s: str) -> bool:
    return bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2})?', s))
