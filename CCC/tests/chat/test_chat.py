"""Test routes related to chat feature of the Flask application."""

from typing import List

import flask
import pytest
from ccc.utils.redis import redis_utils
from flask import Flask
from flask_login import FlaskLoginClient


def test_choose_topics(app: Flask, assistant_client: FlaskLoginClient) -> None:
    with app.test_request_context():
        response = assistant_client.get(flask.url_for("chat_bp.choose_topics"))
        assert response.status_code == 200
        assert b"<p>Welcome assistant.</p>" in response.data


def test_preferred_topics(
    app: Flask, assistant_client: FlaskLoginClient
) -> None:
    with app.test_request_context():
        initial_nb_rooms = len(redis_utils.get_rooms())
        topics = ["movie", "book"]
        response = assistant_client.post(
            flask.url_for("chat_bp.preferred_topics"),
            data={"preferred-topic": topics},
            follow_redirects=True,
        )
        assert len(response.history) == 1
        assert response.request.path == flask.url_for("chat_bp.lobby")

        assert len(redis_utils.get_rooms()) == initial_nb_rooms + len(topics)


def test_preferred_topics_405(
    app: Flask, user_client: FlaskLoginClient
) -> None:
    with app.test_request_context():
        topics = ["sport", "music"]
        response = user_client.post(
            flask.url_for("chat_bp.preferred_topics"),
            data={"preferred-topic": topics},
            follow_redirects=True,
        )
        assert response.status_code == 405


def test_lobby(app: Flask, assistant_client: FlaskLoginClient) -> None:
    with app.test_request_context():
        response = assistant_client.get(flask.url_for("chat_bp.lobby"))
        assert response.status_code == 200
        assert b"<p>Welcome assistant.</p>" in response.data
        assert b"""<div class="row lobby-log"></div>""" in response.data


def test_room(app: Flask, client: FlaskLoginClient) -> None:
    with app.test_request_context():
        response = client.get(
            flask.url_for("chat_bp.room", room_id="Sports and Outdoors:2"),
            follow_redirects=True,
        )
        assert len(response.history) == 1
        assert response.request.path == flask.url_for("auth_bp.login")


def test_room_get(app: Flask, assistant_client: FlaskLoginClient) -> None:
    with app.test_request_context():
        response = assistant_client.get(
            flask.url_for("chat_bp.room", room_id="Sports and Outdoors:2")
        )

        assert response.status_code == 200
        assert (
            b"""<p>\n    Welcome to assistant interface.\n</p>"""
            in response.data
        )


@pytest.mark.parametrize(
    "checklist, nb_tasks, room_id, private_room_id, status_code",
    [
        (
            ["greetings", "search", "qa", "recommend"],
            "4",
            "Sports and Outdoors:2",
            "SportsandOutdoors:2:1",
            302,
        ),
        (
            ["greetings", "qa", "recommend"],
            "4",
            "Sports and Outdoors:2",
            "SportsandOutdoors:2:1",
            200,
        ),
        (
            ["greetings", "search", "qa", "recommend"],
            "2",
            "Sports and Outdoors:2",
            "SportsandOutdoors:2:1",
            500,
        ),
    ],
)
def test_room_leave(
    app: Flask,
    assistant_client: FlaskLoginClient,
    checklist: List[str],
    nb_tasks: str,
    room_id: str,
    private_room_id: str,
    status_code: int,
) -> None:
    """Tests route to leave a room.

    Args:
        app: Flask application.
        assistant_client: Flask client logged as assistant.
        checklist: list of tasks done.
        nb_tasks: total number of tasks to complete.
        room_id: id of the chatroom.
        status_code: expected HTTP response code.
    """
    with app.test_request_context():
        response = assistant_client.post(
            flask.url_for(
                "chat_bp.leave_room",
            ),
            data={
                "checklist": checklist,
                "nb-tasks": nb_tasks,
                "room-id": room_id,
                "private-room-id": private_room_id,
            },
        )

        assert response.status_code == status_code
