"""Tests User class."""


import pytest
from ccc.app.auth.user import User
from ccc.utils.redis import redis_utils
from flask import Flask


def test_get_id(user: User) -> None:
    assert user.get_id() == "username:user0"


def test_get_user_id(assistant: User) -> None:
    assert assistant.get_user_id() == 2


def test_str(assistant: User) -> None:
    assistant_str = assistant.__str__()
    assert (
        assistant_str
        == """{"user_id": 2, "username": "assistant", "role": 1, """
        """"username_key": "username:assistant1"}"""
    )


@pytest.mark.parametrize(
    "name, username, password, role, output",
    [
        ("alice", "test_user", "test_user_pwd", 0, True),
        ("bob", "assistant", "assistant_pwd", 1, False),
    ],
)
def test_register(
    app: Flask, name: str, username: str, password: str, role: int, output: bool
):
    with app.test_request_context():
        registered = User.register(name, username, password, role)
        assert registered == output


def test_user_exists(user: User) -> None:
    username_key = user.get_id()
    assert redis_utils.redis_inst.exists(username_key) == 1

    user_key = redis_utils.redis_inst.get(username_key)
    user_info = redis_utils.hmget(user_key, ["role", "username"])

    assert user.role == int(user_info["role"])
    assert user.username == user_info["username"]


def test_get_by_key(assistant: User) -> None:
    assistant_ = User.get_by_key("username:assistant1")
    assert assistant_ == assistant


def test_get_by_key_wrong() -> None:
    user = User.get_by_key("username:test")
    assert user is None


@pytest.mark.parametrize(
    "password, username_key, output",
    [
        ("test", "username:user0", False),
        ("assistant_pwd", "username:assistant1", True),
    ],
)
def test_login_valid(password: str, username_key: str, output: bool) -> None:
    logged = User.login_valid(password, username_key)
    assert logged == output
