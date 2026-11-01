from datetime import datetime

import pytest
from cron import weekly_report
from cron.weekly_report import KST, build_report, format_index_stats, format_servers

START = datetime(2026, 10, 26, tzinfo=KST)
END = datetime(2026, 11, 1, 23, 59, 59, tzinfo=KST)


def query_results(**overrides):
    results = {
        "save": [{"cnt": "12"}],
        "delete": [{"cnt": "3"}],
        "update": [],
        "live_check": [
            {
                "index": "1",
                "live_start": "5",
                "noti_send": "40",
                "noti_fail": "2",
                "follows": "300",
            },
            {
                "index": "0",
                "live_start": "7",
                "noti_send": "60.0",
                "noti_fail": "0",
                "follows": "450",
            },
        ],
        "servers": [{"servers": "1200"}],
        "servers_prev": [{"servers": "1180"}],
    }
    results.update(overrides)
    return results


@pytest.fixture
def run_queries(mocker):
    return mocker.patch.object(
        weekly_report, "run_queries", return_value=query_results()
    )


class TestBuildReport:
    def test_aggregates_query_results(self, run_queries):
        report = build_report(START, END)

        assert report == {
            "period": {"start": "2026-10-26", "end": "2026-11-01"},
            "notification": {"saved": 12, "deleted": 3, "updated": 0},
            "live_check": {
                "total_live_start": 12,
                "total_noti_send": 100,
                "total_noti_fail": 2,
                "by_index": [
                    {
                        "index": 0,
                        "live_start": 7,
                        "noti_send": 60,
                        "noti_fail": 0,
                        "follows": 450,
                    },
                    {
                        "index": 1,
                        "live_start": 5,
                        "noti_send": 40,
                        "noti_fail": 2,
                        "follows": 300,
                    },
                ],
            },
            "servers": {"current": 1200, "previous": 1180},
        }

    def test_queries_this_week_and_previous_week_for_servers(self, run_queries):
        build_report(START, END)

        specs = run_queries.call_args.args[0]
        assert (specs["save"]["start"], specs["save"]["end"]) == (START, END)
        prev = specs["servers_prev"]
        assert prev["start"] == datetime(2026, 10, 19, tzinfo=KST)
        assert prev["end"] == datetime(2026, 10, 25, 23, 59, 59, tzinfo=KST)

    def test_no_live_check_data(self, run_queries):
        run_queries.return_value = query_results(live_check=[], servers=[])

        report = build_report(START, END)

        assert report["live_check"] == {
            "total_live_start": 0,
            "total_noti_send": 0,
            "total_noti_fail": 0,
            "by_index": [],
        }
        assert report["servers"]["current"] is None


@pytest.mark.parametrize(
    ("current", "previous", "expected"),
    [
        (None, 1000, "`데이터 없음`"),
        (1200, None, "`1,200`개"),
        (1200, 1180, "`1,200`개 (전주 대비 `+20`)"),
        (1180, 1200, "`1,180`개 (전주 대비 `-20`)"),
        (1200, 1200, "`1,200`개 (전주 대비 `0`)"),
    ],
    ids=["no-data", "no-previous", "increase", "decrease", "same"],
)
def test_format_servers(current, previous, expected):
    assert format_servers({"current": current, "previous": previous}) == expected


class TestFormatIndexStats:
    def test_lists_follows_per_index(self):
        stats = [{"index": 0, "follows": 1500}, {"index": 1, "follows": 20}]

        assert format_index_stats(stats) == "`#0` 팔로우 `1,500`명\n`#1` 팔로우 `20`명"

    def test_empty(self):
        assert format_index_stats([]) == "`데이터 없음`"

    def test_truncated_to_embed_field_limit(self):
        stats = [{"index": i, "follows": 1000} for i in range(100)]

        value = format_index_stats(stats)

        assert len(value) <= 1024
        assert value.endswith("\n...")


class TestHandler:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, dynamodb_table, run_queries):
        mocker.patch.object(weekly_report, "table", dynamodb_table.table)
        mocker.patch.object(weekly_report.logger, "info")
        mocker.patch.object(weekly_report.logger, "error")
        return dynamodb_table

    @pytest.fixture
    def send_message(self, mocker):
        return mocker.patch.object(weekly_report, "send_message")

    def get_saved(self, table):
        return table.get_item(Key={"PK": "REPORT#WEEKLY", "SK": "2026-10-26"}).get(
            "Item"
        )

    def test_saves_and_sends_report(self, setup, send_message):
        res = weekly_report.handler({"base_date": "2026-11-04"}, None)

        assert res["statusCode"] == 200
        saved = self.get_saved(setup.table)
        assert saved["type"] == "WEEKLY_REPORT"
        assert saved["period_end"] == "2026-11-01"
        assert saved["notification"] == {"saved": 12, "deleted": 3, "updated": 0}
        assert saved["servers"] == {"current": 1200, "previous": 1180}
        [embed] = send_message.call_args.kwargs["data"]["embeds"]
        assert embed["description"] == "2026-10-26 (월) ~ 2026-11-01 (일)"

    def test_build_failure_alerts_and_skips_save(
        self, setup, run_queries, send_message
    ):
        run_queries.side_effect = TimeoutError("Logs Insights query timeout")

        res = weekly_report.handler({"base_date": "2026-11-04"}, None)

        assert res["statusCode"] == 500
        assert self.get_saved(setup.table) is None
        [embed] = send_message.call_args.kwargs["data"]["embeds"]
        assert embed["title"] == "WEEKLY_REPORT_ERROR"

    def test_save_failure_still_sends_report(self, mocker, setup, send_message):
        mocker.patch.object(
            weekly_report, "save_report", side_effect=RuntimeError("boom")
        )

        res = weekly_report.handler({"base_date": "2026-11-04"}, None)

        assert res == {"statusCode": 500, "error": "Failed: save"}
        titles = [
            c.kwargs["data"]["embeds"][0]["title"] for c in send_message.call_args_list
        ]
        assert titles == ["WEEKLY_REPORT_ERROR", "주간 리포트"]
