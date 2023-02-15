import json

import ccc.app as application
import pytest
from ccc.app.auth.user import User
from ccc.app.chat.room import Room
from ccc.config import TestingConfig
from ccc.utils.redis import redis_utils
from flask import Flask
from flask_login import FlaskLoginClient
from flask_socketio import SocketIOTestClient


@pytest.fixture(scope="module")
def app() -> Flask:
    """Creates the application based on the factory using the testing
    configuration.

    Returns:
        Flask application used to run tests against.
    """
    app = application.create_app(TestingConfig)
    app.test_client_class = FlaskLoginClient
    yield app


@pytest.fixture(scope="module")
def user(app) -> User:
    user = {"id": 1, "name": "alice", "username": "user", "role": 0}
    with app.test_request_context():
        User.register(user["name"], user["username"], "user_pwd", user["role"])
    return User(**user)


@pytest.fixture(scope="module")
def assistant(app) -> User:
    assistant = {"id": 2, "name": "bob", "username": "assistant", "role": 1}
    with app.test_request_context():
        User.register(
            assistant["name"],
            assistant["username"],
            "assistant_pwd",
            assistant["role"],
        )
        assistant_ = User(**assistant)

        # Set preferred topics
        topics = ["sport", "music"]
        user_key = redis_utils.redis_inst.get(assistant_.get_id())
        redis_utils.hmset(user_key, {"topics": ", ".join(topics)})
        redis_utils.create_rooms(assistant_.get_user_id(), topics)

    return assistant_


@pytest.fixture(scope="module")
def client(app: Flask) -> FlaskLoginClient:
    """Creates client to make requests to the application without running the
    server. This client is not logged in.

    Args:
        app: Flask application.

    Returns:
        Client that makes the requests.
    """
    return app.test_client()


@pytest.fixture(scope="module")
def user_client(app: Flask, user: User) -> FlaskLoginClient:
    """Creates client to make requests as a user to the application without
    running the server.

    Args:
        app: Flask application.

    Returns:
        Client that makes the requests.
    """
    return app.test_client(user=user)


@pytest.fixture(scope="module")
def assistant_client(app: Flask, assistant: User) -> FlaskLoginClient:
    """Creates client to make requests as an assistant to the application
    without running the server.

    Args:
        app: Flask application.

    Returns:
        Client that makes the requests.
    """
    return app.test_client(user=assistant)


@pytest.fixture(scope="module")
def room() -> Room:
    id = "Sports and Outdoors:2"

    message_string = json.dumps(
        {
            "from": "bob",
            "msg": "Hello, this is Bob.",
        }
    )
    redis_utils.redis_inst.zadd(f"room:{id}", {message_string: 1654685736068})
    message_string = json.dumps(
        {
            "from": "alice",
            "msg": "Hello, I am Alice.",
        }
    )
    redis_utils.redis_inst.zadd(f"room:{id}", {message_string: 1654686621032})

    return Room(id, max_user=2, topic="Sport and Outdoors")


@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    """Cleanup testing redis db once tests are finished."""

    def remove_redis_db():
        redis_utils.redis_inst.flushdb()

    request.addfinalizer(remove_redis_db)


def get_socketio_client(
    app: Flask, client: FlaskLoginClient, namespace: str
) -> SocketIOTestClient:
    """Creates a socketio client for a specific namespace."""
    socketio_test_client = TestingConfig.socketio.test_client(
        app, flask_test_client=client
    )

    socketio_test_client.connect(namespace)
    return socketio_test_client
