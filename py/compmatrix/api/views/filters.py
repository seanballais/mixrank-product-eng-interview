from datetime import datetime

from compmatrix.utils import dt


def date_filter(date: datetime) -> str | None:
    return dt.dt_to_rfc2822_str(date) if date else None
