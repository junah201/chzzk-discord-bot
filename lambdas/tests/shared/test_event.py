import json

import pytest
from shared.event import (
    get_guild_id,
    get_json_body,
    get_path_param,
    get_token,
)
from shared.exceptions import BadRequestError


class TestGetToken:
    def test_reads_authorization_header(self):
        assert get_token({"headers": {"Authorization": "Bearer t"}}) == "Bearer t"

    @pytest.mark.parametrize(
        "event",
        [{}, {"headers": {}}, {"headers": {"authorization": "Bearer t"}}],
        ids=["no-headers", "empty-headers", "lowercase-key"],
    )
    def test_missing_is_none(self, event):
        assert get_token(event) is None


class TestGetPathParam:
    def test_reads_path_parameter(self):
        assert get_path_param({"pathParameters": {"guild_id": "1"}}, "guild_id") == "1"

    @pytest.mark.parametrize(
        "event",
        [{}, {"pathParameters": None}, {"pathParameters": {}}],
        ids=["no-params", "null-params", "empty-params"],
    )
    def test_missing_is_none(self, event):
        assert get_path_param(event, "guild_id") is None


class TestGetJsonBody:
    def test_parses_object(self):
        assert get_json_body({"body": json.dumps({"a": 1})}) == {"a": 1}

    @pytest.mark.parametrize(
        "event",
        [{}, {"body": None}, {"body": ""}],
        ids=["no-body", "null-body", "empty-body"],
    )
    def test_missing_is_empty_dict(self, event):
        assert get_json_body(event) == {}

    @pytest.mark.parametrize(
        "body",
        ["not-json", "null", "[1, 2]", '"123"'],
        ids=["invalid-json", "json-null", "json-array", "json-string"],
    )
    def test_non_object_raises_bad_request(self, body):
        with pytest.raises(BadRequestError):
            get_json_body({"body": body})


class TestGetGuildId:
    def test_reads_path_parameter(self):
        assert get_guild_id({"pathParameters": {"guild_id": "1"}}) == "1"

    def test_path_takes_precedence_over_body(self):
        event = {
            "pathParameters": {"guild_id": "1"},
            "body": json.dumps({"guild_id": "2"}),
        }

        assert get_guild_id(event) == "1"

    def test_body_is_not_parsed_when_path_has_guild_id(self):
        event = {"pathParameters": {"guild_id": "1"}, "body": "not-json"}

        assert get_guild_id(event) == "1"

    def test_falls_back_to_body(self):
        event = {"pathParameters": None, "body": json.dumps({"guild_id": "2"})}

        assert get_guild_id(event) == "2"

    @pytest.mark.parametrize(
        "event",
        [{}, {"pathParameters": {}, "body": None}, {"body": "{}"}],
        ids=["empty", "body-none", "no-key"],
    )
    def test_missing_is_none(self, event):
        assert get_guild_id(event) is None

    def test_invalid_body_raises_bad_request(self):
        with pytest.raises(BadRequestError):
            get_guild_id({"body": "not-json"})
