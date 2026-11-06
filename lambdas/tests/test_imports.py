"""lambdas/ 아래 모든 모듈을 import 한다.

- 테스트가 없는 모듈도 커버리지 보고서에 잡히게 한다. (lambdas/와 중간 폴더에 __init__.py가 없어서
  coverage가 import되지 않은 파일을 스스로 찾지 못한다.)
- 오타, 순환 import, 빠진 의존성 같은 import 오류를 배포 전에 잡는다.
"""

import importlib
from pathlib import Path

import pytest

LAMBDAS_DIR = Path(__file__).resolve().parents[1]


def find_modules() -> list[str]:
    modules = []
    for path in sorted(LAMBDAS_DIR.rglob("*.py")):
        relative = path.relative_to(LAMBDAS_DIR)
        if relative.parts[0] == "tests" or "__pycache__" in relative.parts:
            continue
        parts = relative.with_suffix("").parts
        if parts[-1] == "__init__":
            parts = parts[:-1]
        if parts:
            modules.append(".".join(parts))
    return modules


MODULES = find_modules()


def test_finds_lambda_modules():
    # 탐색이 깨져서 아무것도 import하지 않는 상황을 막는다.
    assert "shared" in MODULES
    assert "cron.cleanup_orphan_chzzk_channels" in MODULES
    assert "api.notifications.create_notification.service" in MODULES


@pytest.mark.parametrize("module", MODULES)
def test_module_imports(module):
    importlib.import_module(module)
