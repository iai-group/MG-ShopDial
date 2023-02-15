"""Login blueprint of the application."""

from typing import Union

import flask
import flask_login
from ccc.app.auth.user import User
from ccc.utils.redis import redis_utils
from flask import Blueprint, Response

AUTH_BP = Blueprint(
    "auth_bp",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="assets",
)


@AUTH_BP.route("/signup", methods=["GET", "POST"])
def signup() -> Union[Response, str]:
    """User registration.

    Returns:
        Redirect to correct url.
    """
    if flask.request.method == "GET":
        return flask.render_template("auth/signup.html")

    if flask.request.method == "POST":
        name = flask.request.form.get("name")
        username = flask.request.form.get("username")
        password = flask.request.form.get("password")
        role = 0 if flask.request.form.get("role") == "user" else 1

        is_registered = User.register(name, username, password, role)
        if is_registered:
            return flask.redirect(flask.url_for("auth_bp.login"))

    return flask.render_template(
        "auth/signup.html",
        error="Username already exists. Please choose antoher one.",
    )


@AUTH_BP.route("/login", methods=["GET", "POST"])
def login() -> Union[Response, str]:
    """Login if user doesn't exist add it to Redis cache.

    Returns:
        Redirect to correct url.
    """
    if flask.request.method == "GET":
        return flask.render_template("auth/login.html")

    if flask.request.method == "POST":
        username = flask.request.form.get("username")
        password = flask.request.form.get("password")
        role = 0 if flask.request.form.get("role") == "user" else 1

        username_key = redis_utils.make_username_key(username, role)
        user_exists = redis_utils.redis_inst.exists(username_key)
        if not user_exists:
            signup_url = flask.url_for("auth_bp.signup")
            return flask.render_template(
                "auth/login.html",
                error="This username does not exist. Please sign up <a "
                f"href='{signup_url}'>here</a>.",
            )
        else:
            user_key = redis_utils.redis_inst.get(username_key)
            data = redis_utils.redis_inst.hgetall(user_key)
            if User.login_valid(password, username_key):
                user_id = user_key.split(":")[-1]
                logged_user = User(
                    user_id, data["username"], data["name"], int(data["role"])
                )
                flask_login.login_user(logged_user)

                # Check if the shopping assistant already set their favorite
                # topics.
                if role == 1:
                    favorite_topics = (
                        data["topics"] if "topics" in data else None
                    )
                    if not favorite_topics:
                        return flask.redirect(
                            flask.url_for("chat_bp.choose_topics")
                        )
                    else:
                        favorite_topics = favorite_topics.split(", ")
                        redis_utils.create_rooms(
                            logged_user.user_id, favorite_topics
                        )

                return flask.redirect(flask.url_for("chat_bp.lobby"))

    return flask.render_template(
        "auth/login.html", error="Invalid username or password"
    )


@AUTH_BP.route("/logout")
@flask_login.login_required
def logout() -> Response:
    flask_login.logout_user()
    return flask.redirect(flask.url_for("auth_bp.login"))
