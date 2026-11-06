from datetime import datetime, timedelta

import pytest
from cron import send_weekly_report
from cron.send_weekly_report import (
    KST,
    count_query,
    get_count,
    get_servers,
    get_week_range,
    to_epoch,
    to_int,
)


class TestGetWeekRange:
    @pytest.mark.parametrize(
        ("base_date", "expected_start", "expected_end"),
        [
            ("2026-11-02", "2026-10-26", "2026-11-01"),
            ("2026-11-04", "2026-10-26", "2026-11-01"),
            ("2026-11-08", "2026-10-26", "2026-11-01"),
            ("2026-03-01", "2026-02-16", "2026-02-22"),
            ("2026-01-01", "2025-12-22", "2025-12-28"),
            ("2027-01-04", "2026-12-28", "2027-01-03"),
            ("2024-03-04", "2024-02-26", "2024-03-03"),
        ],
        ids=[
            "monday",
            "wednesday",
            "sunday",
            "month-start",
            "year-start",
            "week-spans-new-year",
            "leap-year-february",
        ],
    )
    def test_previous_week_monday_to_sunday(
        self, base_date, expected_start, expected_end
    ):
        start, end = get_week_range({"base_date": base_date})

        assert start == datetime.fromisoformat(expected_start).replace(tzinfo=KST)
        assert end == datetime.fromisoformat(f"{expected_end}T23:59:59").replace(
            tzinfo=KST
        )

    def test_range_is_in_kst(self):
        start, end = get_week_range({"base_date": "2026-11-02"})

        assert start.utcoffset() == timedelta(hours=9)
        assert end.utcoffset() == timedelta(hours=9)
        assert start.isoformat() == "2026-10-26T00:00:00+09:00"
        assert end.isoformat() == "2026-11-01T23:59:59+09:00"

    @pytest.mark.parametrize("event", [None, {}], ids=["none", "empty"])
    def test_without_base_date_uses_now(self, monkeypatch, event):
        # 실제 시계를 쓰면 월요일 0시(KST) 경계에서 결과가 달라지므로 고정한다.
        # UTC로는 일요일이지만 KST로는 월요일이므로 KST 기준 주가 쓰여야 한다.
        fixed_now = datetime(2026, 11, 2, 0, 30, tzinfo=KST)

        class FixedDatetime(datetime):
            @classmethod
            def now(cls, tz=None):
                return fixed_now.astimezone(tz)

        monkeypatch.setattr(send_weekly_report, "datetime", FixedDatetime)

        start, end = get_week_range(event)

        assert start.isoformat() == "2026-10-26T00:00:00+09:00"
        assert end.isoformat() == "2026-11-01T23:59:59+09:00"

    def test_invalid_base_date_raises(self):
        with pytest.raises(ValueError):
            get_week_range({"base_date": "2026/11/02"})


def test_to_epoch():
    assert to_epoch(datetime.fromisoformat("2026-11-02T00:00:00+09:00")) == 1793545200


class TestToInt:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [("3", 3), ("3.0", 3), ("3.9", 3), ("-1.5", -1), (5, 5), (2.7, 2)],
        ids=["int-str", "float-str", "truncated", "negative", "int", "float"],
    )
    def test_converts(self, value, expected):
        assert to_int(value) == expected

    @pytest.mark.parametrize(
        "value",
        [None, "", "abc", [], {}],
        ids=["none", "empty", "text", "list", "dict"],
    )
    def test_invalid_returns_default(self, value):
        assert to_int(value) == 0
        assert to_int(value, default=7) == 7


class TestGetCount:
    def test_reads_cnt_from_first_row(self):
        assert get_count([{"cnt": "12"}, {"cnt": "99"}]) == 12

    @pytest.mark.parametrize("rows", [[], [{}]], ids=["no-rows", "missing-cnt"])
    def test_missing_count_is_zero(self, rows):
        assert get_count(rows) == 0


class TestGetServers:
    def test_reads_servers_from_first_row(self):
        assert get_servers([{"servers": "300"}]) == 300

    @pytest.mark.parametrize(
        "rows", [[], [{}], [{"servers": None}]], ids=["no-rows", "missing", "null"]
    )
    def test_missing_servers_is_none(self, rows):
        assert get_servers(rows) is None

    @pytest.mark.parametrize("value", ["x", "", []], ids=["text", "empty", "list"])
    def test_non_numeric_servers_is_none(self, value):
        assert get_servers([{"servers": value}]) is None

    def test_zero_servers_is_zero(self):
        assert get_servers([{"servers": "0"}]) == 0


def test_count_query():
    assert count_query("SAVE_NOTIFICATION_SUCCESS") == (
        'filter type = "SAVE_NOTIFICATION_SUCCESS" | stats count(*) as cnt'
    )
