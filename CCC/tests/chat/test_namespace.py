"""Tests for the different namespace of the application."""


from typing import Dict

import pytest
from ccc.app.chat.namespace import escape, publish
from flask import Flask
from flask_login import FlaskLoginClient
from tests.conftest import get_socketio_client


@pytest.mark.parametrize(
    "name, message, broadcast, room, namespace",
    [
        (
            "connected",
            {
                "user_id": "1",
                "username": "user",
                "role": "0",
                "username_key": "username:user0",
            },
            True,
            None,
            "/chat",
        ),
        (
            "message",
            {
                "from": "user",
                "message": "test message",
            },
            False,
            "Sports and Outdoors:2",
            "/chat",
        ),
        (
            "log-out",
            {
                "user_id": "1",
                "username": "user",
                "role": "0",
                "username_key": "username:user0",
                "online": False,
                "rooms": '{"room_id": "Sports and Outdoors:2", "participants": '
                '[2], "number_user": 1, "max_user": 2, "has_assistant": false,'
                '"is_full": false}',
            },
            True,
            None,
            "/lobby",
        ),
    ],
)
def test_publish(
    app: Flask,
    user_client: FlaskLoginClient,
    name: str,
    message: Dict,
    broadcast: bool,
    room: str,
    namespace: str,
) -> None:
    with app.app_context() and app.test_request_context():
        socketio_test_client = get_socketio_client(app, user_client, namespace)
        assert socketio_test_client.is_connected(namespace=namespace) is True

        if room:
            socketio_test_client.emit(
                "join", {"room_id": room}, namespace=namespace
            )

        publish(name, message, broadcast, room, namespace)

        response = socketio_test_client.get_received(namespace=namespace)
        assert len(response) == 1
        assert len(response[0]["args"]) == 1
        assert response[0]["name"] == name


def test_escape() -> None:
    message = "Hello 'Alice', 1 > 0."
    processed_msg = escape(message)
    assert processed_msg == "Hello &#39;Alice&#39;, 1 &gt; 0."


# Chat Namespace #
def test_chat_on_connect(app: Flask, user_client: FlaskLoginClient) -> None:
    namespace = "/chat"
    with app.app_context():
        socketio_test_client = get_socketio_client(app, user_client, namespace)
        assert socketio_test_client.is_connected(namespace=namespace) is True

        response = socketio_test_client.get_received(namespace=namespace)
        assert len(response) == 1
        assert response[0]["name"] == "connected"


def test_chat_on_disconnect(app: Flask, user_client: FlaskLoginClient) -> None:
    namespace = "/chat"
    with app.app_context():
        socketio_test_client = get_socketio_client(app, user_client, namespace)

        socketio_test_client.disconnect(namespace=namespace)
        assert socketio_test_client.is_connected(namespace=namespace) is False


def test_chat_on_server_receive() -> None:
    pass


def test_chat_on_join(app: Flask, user_client: FlaskLoginClient) -> None:
    namespace = "/chat"
    with app.app_context():
        socketio_test_client = get_socketio_client(app, user_client, namespace)
        assert socketio_test_client.is_connected(namespace=namespace) is True

        socketio_test_client.emit(
            "join", {"room_id": "Sports and Outdoors:2"}, namespace=namespace
        )

        response = socketio_test_client.get_received(namespace=namespace)
        assert len(response) == 1
        assert response[0]["name"] == "join"


def test_chat_on_leave(app: Flask, user_client: FlaskLoginClient) -> None:
    namespace = "/chat"
    with app.app_context():
        socketio_test_client = get_socketio_client(app, user_client, namespace)
        assert socketio_test_client.is_connected(namespace=namespace) is True

        socketio_test_client.emit(
            "leave",
            {"room_id": "Sports and Outdoors:2", "role": 0, "user_id": 1},
            namespace=namespace,
        )

        response = socketio_test_client.get_received(namespace=namespace)
        assert len(response) == 1
        assert response[0]["name"] == "redirect"


# Lobby Namespace #


def test_lobby_on_connect(app: Flask, user_client: FlaskLoginClient) -> None:
    namespace = "/lobby"
    with app.app_context():
        socketio_test_client = get_socketio_client(app, user_client, namespace)
        assert socketio_test_client.is_connected(namespace=namespace) is True

        response = socketio_test_client.get_received(namespace=namespace)
        assert len(response) == 1
        assert response[0]["name"] == "connected"


def test_lobby_on_log_out(app: Flask, user_client: FlaskLoginClient) -> None:
    namespace = "/lobby"
    with app.app_context():
        socketio_test_client = get_socketio_client(app, user_client, namespace)
        assert socketio_test_client.is_connected(namespace=namespace) is True
        socketio_test_client.emit("log-out", namespace=namespace)

        response = socketio_test_client.get_received(namespace=namespace)
        assert len(response) == 1
        assert response[0]["name"] == "disconnected"


def test_lobby_on_join(app: Flask, user_client: FlaskLoginClient) -> None:
    namespace = "/lobby"
    with app.app_context():
        socketio_test_client = get_socketio_client(app, user_client, namespace)
        assert socketio_test_client.is_connected(namespace=namespace) is True
        socketio_test_client.emit(
            "join", {"room_id": "Sports and Outdoors:2"}, namespace=namespace
        )
        response = socketio_test_client.get_received(namespace=namespace)
        assert len(response) == 1
        assert response[0]["name"] == "join"


def test_lobby_on_join_room() -> None:
    pass
