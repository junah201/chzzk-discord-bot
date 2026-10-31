from decimal import Decimal

import pytest
from shared.dynamodb import dynamo_to_python, python_to_dynamo


class TestDynamoToPython:
    @pytest.mark.parametrize(
        ("attr", "expected"),
        [
            ({"S": "abc"}, "abc"),
            ({"BOOL": True}, True),
            ({"BOOL": False}, False),
            ({"NULL": True}, None),
            ({"N": "42"}, 42),
            ({"N": "-7"}, -7),
            ({"SS": ["a", "b"]}, {"a", "b"}),
        ],
        ids=["S", "BOOL-true", "BOOL-false", "NULL", "N-int", "N-negative", "SS"],
    )
    def test_scalar_types(self, attr, expected):
        assert dynamo_to_python({"k": attr}) == {"k": expected}

    def test_top_level_number_is_int(self):
        result = dynamo_to_python({"k": {"N": "42"}})
        assert type(result["k"]) is int

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [("1.5", 1), ("1.9", 1), ("-2.9", -2)],
    )
    def test_top_level_decimal_number_is_truncated(self, raw, expected):
        # 현재 동작: 소수 N도 int()로 변환되어 0 방향으로 잘린다.
        assert dynamo_to_python({"k": {"N": raw}}) == {"k": expected}

    def test_nested_map_and_list(self):
        item = {
            "m": {
                "M": {"name": {"S": "a"}, "tags": {"L": [{"S": "x"}, {"BOOL": True}]}}
            },
            "l": {"L": [{"M": {"id": {"S": "1"}}}]},
        }
        assert dynamo_to_python(item) == {
            "m": {"name": "a", "tags": ["x", True]},
            "l": [{"id": "1"}],
        }

    def test_nested_numbers_stay_decimal(self):
        # 현재 동작: int 변환은 최상위 N에만 적용되고, M/L 안의 N은 Decimal 그대로다.
        result = dynamo_to_python(
            {"m": {"M": {"n": {"N": "3"}}}, "l": {"L": [{"N": "4"}]}}
        )
        assert result["m"]["n"] == Decimal("3")
        assert type(result["m"]["n"]) is Decimal
        assert type(result["l"][0]) is Decimal

    def test_empty_item(self):
        assert dynamo_to_python({}) == {}


class TestPythonToDynamo:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("abc", {"S": "abc"}),
            (True, {"BOOL": True}),
            (None, {"NULL": True}),
            (42, {"N": "42"}),
            (Decimal("1.5"), {"N": "1.5"}),
            ([1, "x"], {"L": [{"N": "1"}, {"S": "x"}]}),
            ({"a": {"b": "c"}}, {"M": {"a": {"M": {"b": {"S": "c"}}}}}),
        ],
        ids=["S", "BOOL", "NULL", "int", "Decimal", "list", "nested-map"],
    )
    def test_serializes_types(self, value, expected):
        assert python_to_dynamo({"k": value}) == {"k": expected}

    def test_float_is_not_supported(self):
        with pytest.raises(TypeError):
            python_to_dynamo({"k": 1.5})

    def test_empty_item(self):
        assert python_to_dynamo({}) == {}


@pytest.mark.parametrize(
    "item",
    [
        {"PK": "GUILD#1", "SK": "GUILD#1", "current_count": 3, "max_limit": 5},
        {
            "PK": "CHZZK#a",
            "disable_embed": False,
            "custom_message": "",
            "webhook_url": None,
        },
        {"PK": "x", "slot_info": {"previous_slot": "a"}, "tags": ["a", "b"]},
    ],
    ids=["guild", "noti-flags", "nested-without-numbers"],
)
def test_round_trip(item):
    assert dynamo_to_python(python_to_dynamo(item)) == item
