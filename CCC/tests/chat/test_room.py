"""Tests Room class."""
import json

import pytest
from ccc.app.chat.room import Room, RoomEncoder


def test_room_encoder(room: Room) -> None:
    encoder = RoomEncoder()
    room_ = {
        "room_id": "Sports and Outdoors:2",
        "participants": [],
        "number_user": 0,
        "max_user": 2,
        "has_assistant": False,
        "is_full": False,
        "topic": "Sport and Outdoors",
    }
    assert encoder.default(room) == room_


# same test for __repr__()
def test_str(room: Room) -> None:
    room_str = room.__str__()
    room_ = {
        "room_id": "Sports and Outdoors:2",
        "participants": [],
        "number_user": 0,
        "max_user": 2,
        "has_assistant": False,
        "is_full": False,
        "topic": "Sport and Outdoors",
    }
    assert room_str == json.dumps(room_)


@pytest.mark.parametrize(
    "participant, is_assistant, has_assistant, nb_users, is_full",
    [(1, False, False, 1, False), (2, True, True, 2, True)],
)
def test_add_participant(
    room: Room,
    participant: int,
    is_assistant: bool,
    has_assistant: bool,
    nb_users: int,
    is_full: bool,
) -> None:
    assert room.room_status() is False

    room.add_participant(participant, is_assistant)
    assert room.number_user == nb_users
    assert room.has_assistant is has_assistant
    assert room.room_status() is is_full


@pytest.mark.parametrize("participant, is_assistant", [(1, False), (2, True)])
def test_add_participant_raise_exception(
    room: Room,
    participant: int,
    is_assistant: bool,
) -> None:
    assert room.room_status() is True
    with pytest.raises(RuntimeError):
        room.add_participant(participant, is_assistant)


@pytest.mark.parametrize(
    "participant, is_assistant, has_assistant, nb_users, is_full",
    [(1, False, True, 1, False), (2, True, False, 0, False)],
)
def test_remove_participant(
    room: Room,
    participant: int,
    is_assistant: bool,
    has_assistant: bool,
    nb_users: int,
    is_full: bool,
) -> None:
    room.remove_participant(participant, is_assistant)
    assert room.number_user == nb_users
    assert room.has_assistant is has_assistant
    assert room.room_status() is is_full


@pytest.mark.parametrize("participant, is_assistant", [(5, False), (2, True)])
def test_remove_participant_raises_exception(
    room: Room, participant: int, is_assistant: bool
) -> None:
    with pytest.raises(RuntimeError):
        room.remove_participant(participant, is_assistant)
