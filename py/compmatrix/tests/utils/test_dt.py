from datetime import datetime, timezone

from compmatrix.utils import dt


def test_dt_to_rfc2822_str():
    dt_obj = datetime(2013, 8, 14, 0, 42, 26, tzinfo=timezone.utc)
    assert dt.dt_to_rfc2822_str(dt_obj) == '2013-08-14 00:42:26UTC'
