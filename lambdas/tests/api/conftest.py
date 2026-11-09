import importlib

import pytest
from shared.discord.utils import AdminCheckResult

middleware_module = importlib.import_module("shared.middleware")


@pytest.fixture
def as_admin(mocker):
    """require_guild_admin=True 핸들러에서 요청한 유저를 서버 관리자로 통과시킨다."""
    return mocker.patch.object(
        middleware_module, "is_admin", return_value=AdminCheckResult(True, 200)
    )
