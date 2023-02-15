"""Coached Conversation Collector application.

Flask application to collect conversations between clients and shopping
assistants.

Redis integration is based on this repository:
https://github.com/alexsmartens/simple-chat-app.
"""

import os

import ccc.app as application
import ccc.config as config
import flask
from ccc.app.chat.namespace import ChatNamespace, LobbyNamespace
from flask import Response
from werkzeug.middleware.proxy_fix import ProxyFix

env = os.environ["FLASK_ENV"]
app_config = config.get_config(env)
app = application.create_app(app_config)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

socketio = app_config.socketio


@app.route("/")
def index() -> Response:
    return flask.redirect(flask.url_for("auth_bp.login"))


@app.route("/tou")
def terms_of_use() -> Response:
    return flask.render_template("terms.html")


@socketio.on_error_default
def default_error_handler(e):
    """Handle error for all namespaces."""
    app.logger.error(e)


socketio.on_namespace(ChatNamespace(application.CHAT_NAMESPACE))
socketio.on_namespace(LobbyNamespace(application.LOBBY_NAMESPACE))

if __name__ == "__main__":
    app.run()
