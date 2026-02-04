from typing import Dict, Any, Iterable


def pick(data: Dict[str, Any], keys: Iterable[str]) -> Dict[str, Any]:
    """
    딕셔너리에서 지정된 키(keys)만 추출하여 새로운 딕셔너리를 반환합니다.
    데이터에 해당 키가 없으면 무시합니다.

    Usage:
        pick(user_data, ['id', 'name'])
    """
    if not data:
        return {}

    return {k: data[k] for k in keys if k in data}


def omit(data: Dict[str, Any], keys: Iterable[str]) -> Dict[str, Any]:
    """
    딕셔너리에서 지정된 키(keys)를 제외한 나머지 데이터를 반환합니다.

    Usage:
        omit(user_data, ['password', 'private_token'])
    """
    if not data:
        return {}

    keys_set = set(keys)
    return {k: v for k, v in data.items() if k not in keys_set}
