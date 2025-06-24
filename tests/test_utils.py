from src.utils import get_date_range
from datetime import datetime
import pytest


# Тесты для get_date_range
@pytest.mark.parametrize("date_str, range_type, expected_start, expected_end", [
    # Месяц: 2021-12
    ("2021-12-31", "M", datetime(2021, 12, 1), datetime(2021, 12, 31)),

    # Неделя: 2021-12-27 – 2022-01-02
    ("2021-12-31", "W", datetime(2021, 12, 27), datetime(2022, 1, 2)),

    # Год: 2021-01-01 – 2021-12-31
    ("2021-05-15", "Y", datetime(2021, 1, 1), datetime(2021, 12, 31)),

    # ALL: с 2000-01-01 по указанную дату
    ("2021-05-15", "ALL", datetime(2000, 1, 1), datetime(2021, 5, 15)),
])
def test_get_date_range(date_str, range_type, expected_start, expected_end):
    start, end = get_date_range(date_str, range_type)

    assert start.date() == expected_start.date()
    assert end.date() == expected_end.date()
