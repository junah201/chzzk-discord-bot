import importlib
import json

import pytest

chzzk_unfollow = importlib.import_module("admin.chzzk_unfollow")

CHZZK_ID = "abc"


@pytest.fixture(autouse=True)
def ddb(mocker, dynamodb_table):
    mocker.patch.object(chzzk_unfollow, "table", dynamodb_table.table)
    for index in (2, 5):
        dynamodb_table.table.put_item(
            Item={
                "PK": "NAVER#ACCOUNTS",
                "SK": f"NAVER#{index}",
                "type": "NAVER",
                "NID_AUT": f"fake-aut-{index}",
                "NID_SES": f"fake-ses-{index}",
            }
        )
    return dynamodb_table


@pytest.fixture(autouse=True)
def unfollow(mocker):
    return mocker.patch.object(
        chzzk_unfollow, "unfollow_chzzk_channel", return_value=(True, 200, "")
    )


def call(**event):
    res = chzzk_unfollow.handler(event, None)
    return res, json.loads(res["body"])


def put_chzzk(table, **attrs):
    table.put_item(
        Item={
            "PK": f"CHZZK#{CHZZK_ID}",
            "SK": f"CHZZK#{CHZZK_ID}",
            "type": "CHZZK",
            **attrs,
        }
    )


def test_uses_account_stored_on_chzzk_item(ddb, unfollow):
    put_chzzk(ddb.table, index=5)

    res, _ = call(chzzk_id=CHZZK_ID)

    assert res["statusCode"] == 200
    unfollow.assert_called_once_with(CHZZK_ID, "fake-aut-5", "fake-ses-5")


def test_explicit_index_skips_lookup(unfollow):
    res, _ = call(chzzk_id=CHZZK_ID, index=2)

    assert res["statusCode"] == 200
    unfollow.assert_called_once_with(CHZZK_ID, "fake-aut-2", "fake-ses-2")


@pytest.mark.parametrize(
    ("event", "chzzk_attrs", "message"),
    [
        ({}, None, "'chzzk_id' is required in the event."),
        (
            {"chzzk_id": CHZZK_ID},
            None,
            f"치지직 채널 '{CHZZK_ID}'은 등록되지 않았습니다.",
        ),
        (
            {"chzzk_id": CHZZK_ID},
            {},
            f"치지직 채널 '{CHZZK_ID}'의 'index' 정보가 없습니다.",
        ),
        (
            {"chzzk_id": CHZZK_ID, "index": 6},
            None,
            "인덱스 '6'에 해당하는 네이버 계정이 없습니다.",
        ),
    ],
    ids=["no-chzzk-id", "not-registered", "no-index", "no-account"],
)
def test_invalid_input_is_400(ddb, unfollow, event, chzzk_attrs, message):
    if chzzk_attrs is not None:
        put_chzzk(ddb.table, **chzzk_attrs)

    res, body = call(**event)

    assert res["statusCode"] == 400
    assert body["message"] == message
    unfollow.assert_not_called()


def test_unfollow_failure_returns_its_status(unfollow):
    unfollow.return_value = (False, 404, "채널 없음")

    res, body = call(chzzk_id=CHZZK_ID, index=2)

    assert res["statusCode"] == 404
    assert body["message"].endswith("팔로우 해제에 실패했습니다: 채널 없음")
