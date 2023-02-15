"""Admin blueprint of the application."""

from typing import Dict

import flask
from ccc.utils.redis import redis_utils
from flask import Blueprint

ADMIN_BP = Blueprint(
    "admin_bp",
    __name__,
    template_folder="templates",
)


@ADMIN_BP.route("/", methods=["GET", "POST"])
def access_admin() -> str:
    """Asks passphrase to access Admin dashboard."""

    if flask.request.method == "POST":
        passphrase = flask.request.form.get("passphrase")
        admin_passphrase = redis_utils.get_admin_passphrase()
        if passphrase == admin_passphrase:
            online_users = redis_utils.get_online_users()
            conversations = redis_utils.retrieve_conversations()
            rooms = redis_utils.get_rooms()

            return flask.render_template(
                "admin/admin.html",
                is_authorized=True,
                online_users=online_users,
                conversations=conversations,
                rooms=rooms,
            )
        else:
            return flask.render_template(
                "admin/admin.html",
                is_authorized=False,
                error="Invalid passphrase.",
            )

    return flask.render_template("admin/admin.html", is_authorized=False)


@ADMIN_BP.route("/conversation", methods=["POST"])
def get_conversation_log() -> Dict[int, str]:
    """Retrieves conversation log.

    Returns:
        List of messages wrapped in a Response object.
    """
    room_id = flask.request.form.get("room")
    messages = redis_utils.get_messages(room_id, offset=0, size=50)
    log = dict()
    for i, message in enumerate(messages):
        sender = message["from"].upper()
        msg = message["msg"]
        log[i] = f"{sender}: {msg}"

    return flask.jsonify(log)
