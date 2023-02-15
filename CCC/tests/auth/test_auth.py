"""Test authentication routes of the Flask application."""
import flask
import pytest
from flask import Flask
from flask_login import FlaskLoginClient


def test_login_get(app: Flask, assistant_client: FlaskLoginClient) -> None:
    with app.test_request_context():
        response = assistant_client.get(flask.url_for("auth_bp.login"))
        assert response.status_code == 200
        assert b"<strong>Error:</strong>" not in response.data


@pytest.mark.parametrize(
    "username, password, role, redirection",
    [
        ("user1", "user1_pwd", "user", "chat_bp.lobby"),
        ("assistant1", "assistant1_pwd", "assistant", "chat_bp.choose_topics"),
        ("user", "user_pwd", "user", "chat_bp.lobby"),
        ("assistant", "assistant_pwd", "assistant", "chat_bp.lobby"),
    ],
)
def test_login_post(
    app: Flask,
    client: FlaskLoginClient,
    username: str,
    password: str,
    role: str,
    redirection: str,
) -> None:
    with app.test_request_context():
        response = client.post(
            flask.url_for("auth_bp.login"),
            data={"username": username, "password": password, "role": role},
            follow_redirects=True,
        )
        assert len(response.history) == 1
        assert response.request.path == flask.url_for(redirection)


def test_login_wrong_password(app: Flask, client: FlaskLoginClient) -> None:
    with app.test_request_context():
        response = client.post(
            flask.url_for("auth_bp.login"),
            data={"username": "user", "password": "wrong_pwd", "role": "user"},
        )

        assert response.status_code == 200
        assert b"<strong>Error:</strong>" in response.data


def test_logout(app: Flask, user_client: FlaskLoginClient) -> None:
    with app.test_request_context():
        response = user_client.get(
            flask.url_for("auth_bp.logout"), follow_redirects=True
        )
        assert len(response.history) == 1
        assert response.request.path == flask.url_for("auth_bp.login")
