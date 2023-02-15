"""Test utils functions to interact with Redis."""
from typing import Dict, List

import pytest
from ccc.utils.redis import redis_utils
from ccc.app.chat.room import Room


def test_get_passphrase() -> None:
    assert "passphrase" == redis_utils.get_admin_passphrase()


@pytest.mark.parametrize(
    "username, role, output",
    [("user", 0, "username:user0"), ("test", 1, "username:test1")],
)
def test_make_username_key(username: str, role: int, output: str) -> None:
    key = redis_utils.make_username_key(username, role)
    assert key == output


@pytest.mark.parametrize(
    "username_key, b_exist",
    [("username:user0", True), ("username:user23", False)],
)
def test_user_exists(username_key: str, b_exist: bool) -> None:
    assert bool(redis_utils.user_exists(username_key)) == b_exist


def test_get_online_users() -> None:
    assert not redis_utils.get_online_users()


def test_retrieve_conversations() -> None:
    assert not redis_utils.retrieve_conversations()


@pytest.mark.parametrize(
    "room, messages",
    [
        ("1:2", []),
        (
            "Sports and Outdoors:2",
            [
                {
                    "from": "bob",
                    "msg": "Hello, this is Bob.",
                },
                {
                    "from": "alice",
                    "msg": "Hello, I am Alice.",
                },
            ],
        ),
    ],
)
def test_get_messages(room: str, messages: List[Dict]) -> None:
    messages_ = redis_utils.get_messages(room)

    diff_msg = False
    for m in messages:
        if m not in messages_:
            diff_msg = True

    assert diff_msg is False
    assert len(messages_) == len(messages)


def test_get_private_room_id(room: Room) -> None:
    """
    Args:
        room: chatroom
    """
    assert redis_utils.get_private_room_id(room) == "SportsandOutdoors:2"


def test_get_private_room_id2(room: Room) -> None:
    """
    Args:
        room: chatroom
    """
    room.add_participant(2, True)
    assert redis_utils.get_private_room_id(room) == "SportsandOutdoors:2"

    room.add_participant(1, False)
    assert redis_utils.get_private_room_id(room) == "SportsandOutdoors:2:1"


def test_add_participants_rooms_raise_exception() -> None:
    with pytest.raises(RuntimeError):
        redis_utils.add_participants_rooms("test_room:2")


def test_add_participants_rooms() -> None:
    room_id = "test_room:2:1"
    redis_utils.add_participants_rooms(room_id)

    assert room_id in redis_utils.redis_inst.smembers("user:1:rooms")
    assert room_id in redis_utils.redis_inst.smembers("user:2:rooms")
