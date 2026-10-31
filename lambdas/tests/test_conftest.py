import os
import socket

import pytest


def test_aws_env_uses_fake_credentials():
    assert os.environ["AWS_ACCESS_KEY_ID"] == "testing"
    assert "AWS_PROFILE" not in os.environ


def test_real_network_connection_is_blocked():
    with (
        socket.socket() as sock,
        pytest.raises(RuntimeError, match="실제 네트워크 연결"),
    ):
        sock.connect(("127.0.0.1", 9))
