import json
from datetime import UTC, datetime, timedelta, timezone

import pytest
from shared.utils import build_response, mask_secret, omit, pick, to_kst_string


class TestPick:
    def test_returns_only_requested_keys(self):
        assert pick({"a": 1, "b": 2, "c": 3}, ["a", "c"]) == {"a": 1, "c": 3}

    def test_ignores_missing_keys(self):
        assert pick({"a": 1, "b": 2}, ["a", "z"]) == {"a": 1}

    @pytest.mark.parametrize("data", [{}, None], ids=["empty", "none"])
    def test_empty_data_returns_empty_dict(self, data):
        assert pick(data, ["a"]) == {}

    def test_accepts_any_iterable_of_keys(self):
        assert pick({"a": 1, "b": 2}, (k for k in "ab")) == {"a": 1, "b": 2}

    def test_does_not_mutate_input(self):
        data = {"a": 1, "b": 2}
        pick(data, ["a"])
        assert data == {"a": 1, "b": 2}


class TestOmit:
    def test_removes_given_keys(self):
        assert omit({"a": 1, "b": 2, "c": 3}, ["b"]) == {"a": 1, "c": 3}

    def test_ignores_missing_keys(self):
        assert omit({"a": 1}, ["z"]) == {"a": 1}

    @pytest.mark.parametrize("data", [{}, None], ids=["empty", "none"])
    def test_empty_data_returns_empty_dict(self, data):
        assert omit(data, ["a"]) == {}

    def test_accepts_any_iterable_of_keys(self):
        assert omit({"a": 1, "b": 2, "c": 3}, (k for k in "ab")) == {"c": 3}


class TestBuildResponse:
    def test_204_has_no_body(self):
        assert build_response(204, "ignored", {"a": 1}) == {"statusCode": 204}

    def test_message_only(self):
        res = build_response(400, "잘못된 요청")
        assert res["statusCode"] == 400
        assert json.loads(res["body"]) == {"message": "잘못된 요청"}

    @pytest.mark.parametrize("data", [{"a": 1}, [1, 2]], ids=["dict", "list"])
    def test_data_only_becomes_body(self, data):
        res = build_response(200, data=data)
        assert json.loads(res["body"]) == data

    def test_no_message_and_no_data_is_empty_object(self):
        assert build_response(200) == {"statusCode": 200, "body": "{}"}

    def test_data_replaces_message(self):
        # 의도한 동작: data가 있으면 message는 body에서 빠진다.
        res = build_response(200, "msg", {"a": 1})
        assert json.loads(res["body"]) == {"a": 1}

    @pytest.mark.parametrize("data", [{}, []], ids=["empty-dict", "empty-list"])
    def test_empty_data_is_returned_as_is(self, data):
        res = build_response(200, data=data)
        assert json.loads(res["body"]) == data

    def test_empty_data_also_replaces_message(self):
        res = build_response(200, "msg", [])
        assert json.loads(res["body"]) == []

    def test_body_keeps_non_ascii_characters(self):
        res = build_response(200, "한글")
        assert "한글" in res["body"]


class TestToKstString:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("2026-01-01T00:00:00Z", "2026-01-01 09:00:00"),
            ("2026-01-01T00:00:00+00:00", "2026-01-01 09:00:00"),
            ("2026-01-01T00:00:00", "2026-01-01 09:00:00"),
            (datetime(2026, 1, 1, 0, 0), "2026-01-01 09:00:00"),
            (datetime(2026, 1, 1, 0, 0, tzinfo=UTC), "2026-01-01 09:00:00"),
            (
                datetime(2026, 1, 1, 0, 0, tzinfo=timezone(timedelta(hours=-5))),
                "2026-01-01 14:00:00",
            ),
        ],
        ids=[
            "z-suffix",
            "utc-offset",
            "naive-str",
            "naive-dt",
            "utc-dt",
            "other-tz-dt",
        ],
    )
    def test_converts_utc_to_kst(self, value, expected):
        assert to_kst_string(value) == expected

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("2026-03-31T15:00:00Z", "2026-04-01 00:00:00"),
            ("2026-12-31T15:00:00Z", "2027-01-01 00:00:00"),
            ("2026-12-31T14:59:59Z", "2026-12-31 23:59:59"),
        ],
        ids=["month-end", "year-end", "just-before-midnight"],
    )
    def test_date_boundaries(self, value, expected):
        assert to_kst_string(value) == expected

    def test_custom_format(self):
        assert to_kst_string("2026-01-01T00:00:00Z", "%Y/%m/%d") == "2026/01/01"

    @pytest.mark.parametrize("value", ["", None, 0], ids=["empty", "none", "zero"])
    def test_falsy_returns_empty_string(self, value):
        assert to_kst_string(value) == ""

    def test_unsupported_type_is_stringified(self):
        assert to_kst_string(5) == "5"

    def test_invalid_string_raises(self):
        with pytest.raises(ValueError):
            to_kst_string("not-a-date")


class TestMaskSecret:
    def test_keeps_both_ends(self):
        assert mask_secret("AAAAbbbbbbbbbbbbZZZZ") == "AAAA...ZZZZ"

    def test_custom_visible_length(self):
        assert mask_secret("abcdefghijklmnop", visible=2) == "ab...op"

    @pytest.mark.parametrize("value", ["a", "abcdefgh"], ids=["one-char", "exactly-8"])
    def test_short_value_is_fully_masked(self, value):
        assert mask_secret(value) == "***"

    def test_nine_chars_shows_ends(self):
        assert mask_secret("abcdefghi") == "abcd...fghi"

    @pytest.mark.parametrize("value", [None, ""], ids=["none", "empty"])
    def test_empty_value_is_returned_as_is(self, value):
        assert mask_secret(value) == value

    def test_does_not_leak_middle(self):
        secret = "AAAA" + "secret-middle-part" + "ZZZZ"
        assert "secret-middle-part" not in mask_secret(secret)
