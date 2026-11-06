import importlib
import json

import pytest

backfill = importlib.import_module("admin.noti_chzzk_id_backfill")


@pytest.fixture(autouse=True)
def ddb(mocker, dynamodb_table):
    mocker.patch.object(backfill, "table", dynamodb_table.table)
    table = dynamodb_table.table
    table.put_item(
        Item={"PK": "CHZZK#old", "SK": "NOTI#1", "type": "NOTI", "guild_id": "g"}
    )
    table.put_item(
        Item={
            "PK": "CHZZK#new",
            "SK": "NOTI#2",
            "type": "NOTI",
            "guild_id": "g",
            "chzzk_id": "new",
        }
    )
    table.put_item(Item={"PK": "CHZZK#old", "SK": "CHZZK#old", "type": "CHZZK"})
    return dynamodb_table


def call(**event):
    res = backfill.handler(event, None)
    return res, json.loads(res["body"])


def get(table, pk, sk):
    return table.get_item(Key={"PK": pk, "SK": sk})["Item"]


def test_dry_run_by_default_writes_nothing(ddb):
    res, body = call()

    assert res["statusCode"] == 200
    assert body["dry_run"] is True
    assert body["found"] == 1
    assert body["updated"] == 0
    assert body["sample"] == [{"PK": "CHZZK#old", "SK": "NOTI#1"}]
    assert "chzzk_id" not in get(ddb.table, "CHZZK#old", "NOTI#1")


def test_fills_chzzk_id_from_pk(ddb):
    _, body = call(dry_run=False)

    assert body["found"] == 1
    assert body["updated"] == 1
    assert get(ddb.table, "CHZZK#old", "NOTI#1")["chzzk_id"] == "old"
    assert get(ddb.table, "CHZZK#new", "NOTI#2")["chzzk_id"] == "new"
    assert "chzzk_id" not in get(ddb.table, "CHZZK#old", "CHZZK#old")


def test_second_run_finds_nothing():
    call(dry_run=False)

    _, body = call(dry_run=False)

    assert body["found"] == 0
    assert body["updated"] == 0


def test_item_deleted_after_scan_is_not_recreated(ddb, mocker):
    items = list(backfill.scan_notis_without_chzzk_id())
    ddb.table.delete_item(Key={"PK": "CHZZK#old", "SK": "NOTI#1"})
    mocker.patch.object(backfill, "scan_notis_without_chzzk_id", return_value=items)

    _, body = call(dry_run=False)

    assert body["updated"] == 0
    assert "Item" not in ddb.table.get_item(Key={"PK": "CHZZK#old", "SK": "NOTI#1"})


def test_non_bool_dry_run_is_500():
    res, _ = call(dry_run="false")

    assert res["statusCode"] == 500
