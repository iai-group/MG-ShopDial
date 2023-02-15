"""Flask factory creating the application."""

import logging
import os
from pathlib import Path
from typing import Union

import ccc.utils.es.es_utils as es_utils
import ccc.utils.redis.redis_utils as redis_utils
from ccc.app.auth.user import User
from ccc.app.chat.topics import load_topics
from ccc.config import DevelopmentConfig
from flask import Flask
from flask_login import LoginManager

login_manager = LoginManager()
TOPICS = load_topics(Path(__file__).parent / "chat/static/yml/topics.yml", n=50)
CHAT_NAMESPACE = "/chat"
LOBBY_NAMESPACE = "/lobby"


def create_app(config=DevelopmentConfig) -> Flask:
    """Creates application with specified configuration.

    Args:
        config: Application configuration.

    Returns:
        Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(config)

    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    with app.app_context():
        config.socketio.init_app(
            app, cors_allowed_origins="*", async_mode="eventlet"
        )
        login_manager.login_view = "auth_bp.login"
        login_manager.init_app(app)

        redis_utils.init_redis(os.environ.get("FLASK_ENV"))
        es_utils.init_elasticsearch(os.environ.get("FLASK_ENV"))

        from ccc.app.admin import admin
        from ccc.app.auth import auth
        from ccc.app.chat import chat

        app.register_blueprint(auth.AUTH_BP, url_prefix="/auth")
        app.register_blueprint(chat.CHAT_BP, url_prefix="/chat")
        app.register_blueprint(admin.ADMIN_BP, url_prefix="/admin")

    return app


@login_manager.user_loader
def load_user(user_id) -> Union[User, None]:
    return User.get_by_key(user_id)
