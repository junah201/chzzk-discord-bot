import os
import socket
from types import SimpleNamespace

import boto3
import pytest
import responses
from moto import mock_aws

# 일부 모듈이 import 시점에 boto3 클라이언트를 만들고 환경 변수를 읽으므로,
# 테스트 모듈이 import 되기 전에 테스트용 값으로 덮어쓴다.
os.environ["AWS_DEFAULT_REGION"] = "ap-northeast-2"
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["AWS_EC2_METADATA_DISABLED"] = "true"
# 로컬의 `chzzk` 프로필이나 설정 파일이 섞이지 않게 한다.
os.environ.pop("AWS_PROFILE", None)
os.environ["AWS_CONFIG_FILE"] = os.devnull
os.environ["AWS_SHARED_CREDENTIALS_FILE"] = os.devnull

os.environ["DISCORD_PUBLIC_KEY"] = "test-discord-public-key"
os.environ["DISCORD_TOKEN"] = "test-discord-token"
os.environ["DISCORD_CLIENT_ID"] = "test-discord-client-id"
os.environ["DISCORD_CLIENT_SECRET"] = "test-discord-client-secret"
os.environ["ADMIN_DISCORD_PUBLIC_KEY"] = "test-admin-discord-public-key"
os.environ["ADMIN_DISCORD_USER_ID"] = "1"
os.environ["ADMIN_DISCORD_TOKEN"] = "test-admin-discord-token"
os.environ["KOREANBOTS_TOKEN"] = "test-koreanbots-token"
for _name in (
    "DISCORD_NAVER_SESSION_RENEW_EXPIRED_CHANNEL_ID",
    "DISCORD_GET_FOLLOWING_ERROR_CHANNEL_ID",
    "DISCORD_CHZZK_FOLLOW_ERROR_CHANNEL_ID",
    "DISCORD_KOREANBOTS_UPDATE_STATS_ERROR_CHANNEL_ID",
    "DISCORD_CLEANUP_ORPHAN_CHANNEL_ID",
    "DISCORD_WEEKLY_REPORT_CHANNEL_ID",
    "DISCORD_WEEKLY_REPORT_ERROR_CHANNEL_ID",
):
    os.environ[_name] = "100000000000000000"


class NetworkAccessError(RuntimeError):
    pass


@pytest.fixture(autouse=True)
def block_network(monkeypatch):
    """실제 네트워크 연결을 막는다. 외부 호출은 반드시 mock 해야 한다."""

    def guarded_connect(_self, address, *_args, **_kwargs):
        raise NetworkAccessError(f"테스트에서 실제 네트워크 연결 시도: {address}")

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
    monkeypatch.setattr(socket.socket, "connect_ex", guarded_connect)


@pytest.fixture
def mock_requests():
    """requests 호출을 가로챈다. 등록하지 않은 요청이나 호출되지 않은 응답이 있으면 실패한다."""
    with responses.RequestsMock() as rsps:
        yield rsps


TABLE_NAME = "chzzk-bot-db"


@pytest.fixture
def dynamodb_table():
    """moto로 띄운 chzzk-bot-db 테이블. 테스트마다 새로 만들어서 상태를 공유하지 않는다.

    모듈 전역 boto3 객체는 import 시점(moto 활성화 이전)에 만들어지므로,
    테스트에서 mocker.patch.object(module, "dynamodb", dynamodb_table.client)처럼 교체해서 쓴다.
    """
    with mock_aws():
        client = boto3.client("dynamodb")
        client.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
                {"AttributeName": "guild_id", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "GSI-GuildID-v2",
                    "KeySchema": [
                        {"AttributeName": "guild_id", "KeyType": "HASH"},
                        {"AttributeName": "PK", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        resource = boto3.resource("dynamodb")
        yield SimpleNamespace(
            client=client, resource=resource, table=resource.Table(TABLE_NAME)
        )
