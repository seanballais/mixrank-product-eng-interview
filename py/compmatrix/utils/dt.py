from datetime import datetime


def dt_to_rfc2822_str(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%d %H:%M:%S%Z')
