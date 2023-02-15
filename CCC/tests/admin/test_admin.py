"""Test admin side of the Flask application."""
from typing import Dict

import flask
import pytest
from flask import Flask
from flask_login import FlaskLoginClient


def test_access_admin_get(app: Flask, client: FlaskLoginClient) -> None:
    with app.test_request_context():
        response = client.get(flask.url_for("admin_bp.access_admin"))
        assert response.status_code == 200
        assert (
            b'<label for="password" class="col-form-label col-sm-6">Enter '
            b"passphrase to access Admin" in response.data
        )


def test_access_admin_wrong_passphrase(
    app: Flask, client: FlaskLoginClient
) -> None:
    with app.test_request_context():
        response = client.post(
            flask.url_for("admin_bp.access_admin"),
            data={"passphrase": "pasphrase"},
        )
        assert response.status_code == 200
        assert (
            b'<label for="password" class="col-form-label col-sm-6">Enter '
            b"passphrase to access Admin" in response.data
        )
        assert b"<strong>Error:</strong>" in response.data


def test_access_admin_post(app: Flask, client: FlaskLoginClient) -> None:
    with app.test_request_context():
        response = client.post(
            flask.url_for("admin_bp.access_admin"),
            data={"passphrase": "passphrase"},
        )
        assert response.status_code == 200
        assert b"<p>Number of room opened: 0</p>" in response.data


@pytest.mark.parametrize(
    "room, conversation",
    [
        (
            "Sports and Outdoors:2",
            {
                0: "BOB: Hello, this is Bob.",
                1: "ALICE: Hello, I am Alice.",
            },
        ),
        ("sport", {}),
    ],
)
def test_get_conversation_log(
    app: Flask, client: FlaskLoginClient, room: str, conversation: Dict
) -> None:
    with app.test_request_context():
        response = client.post(
            flask.url_for("admin_bp.get_conversation_log"),
            data={"room": room},
        )
        print(response)
        assert conversation == response.json
