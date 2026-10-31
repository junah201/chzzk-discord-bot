from shared.utils import pick


def test_pick_ignores_missing_keys():
    assert pick({"a": 1, "b": 2}, ["a", "c"]) == {"a": 1}
