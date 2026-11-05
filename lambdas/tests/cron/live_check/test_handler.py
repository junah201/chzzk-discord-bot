import importlib
import json

from cron.live_check.logic import LiveCheckStats

live_check = importlib.import_module("cron.live_check")

EVENT = {
    "resources": ["arn:aws:events:ap-northeast-2:123:rule/live_check_trigger_for_3"]
}


def test_runs_with_index_from_rule_name(mocker):
    mocker.patch.object(live_check.logger, "info")
    run = mocker.patch.object(
        live_check,
        "run",
        return_value=LiveCheckStats(
            index=3,
            total_follows_count=3,
            total_live_channels_count=2,
            total_live_start_cnt=2,
            total_noti_send_cnt=2,
            total_noti_fail_cnt=1,
        ),
    )

    res = live_check.handler(EVENT, None)

    assert run.call_args.args[0] == 3
    assert res["statusCode"] == 200
    assert json.loads(res["body"]) == {
        "index": 3,
        "total_follows_count": 3,
        "total_live_channels_count": 2,
        "total_live_start_cnt": 2,
        "total_noti_send_cnt": 2,
        "total_noti_fail_cnt": 1,
    }
