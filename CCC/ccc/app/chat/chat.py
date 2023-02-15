"""Chat blueprint of the application."""

import json
import os
from typing import Any, Dict, List

import ccc.utils.es.es_utils as es_utils
import ccc.utils.redis.redis_utils as redis_utils
import flask
import flask_login
from ccc import app
from flask import Blueprint, Response

CHAT_BP = Blueprint(
    "chat_bp",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="assets",
)


@CHAT_BP.route("/room/<string:room_id>", methods=["GET"])
@CHAT_BP.route("/room/<string:room_id>/<int:scenario_id>", methods=["GET"])
@flask_login.login_required
def room(room_id=None, scenario_id=None) -> str:
    """Displays the user or shopping assistant chat interface.

    Args:
        room_id: Room where the experiment will take place.
        scenario_id: Scenario id of the room.

    Returns:
        Render the interface according to worker's role.
    """
    user = flask_login.current_user
    room = redis_utils.get_room_by_id(room_id)
    scenario = app.TOPICS.get_scenario(room.topic, scenario_id)

    if not app.TOPICS.have_scenario(room.topic):
        redis_utils.remove_room(room)
        flask.flash("This room is not available anymore.")
        return flask.redirect(flask.url_for("chat_bp.lobby"))

    if user.role == "0":
        try:
            if not scenario_id:
                scenario = app.TOPICS.get_random_scenario(room.topic)

            return flask.render_template(
                "chat/ui.html",
                user=user,
                room=room_id,
                room_status=room.is_full,
                scenario=scenario,
            )
        except IndexError:
            flask.flash("This room is not available anymore.")
            return flask.redirect(flask.url_for("chat_bp.lobby"))
    elif user.role == "1":
        products = load_product(room.topic)
        return flask.render_template(
            "chat/assistant_ui.html",
            user=user,
            room=room_id,
            room_status=room.is_full,
            products=products,
            scenario=scenario if scenario is not None else {},
        )

    flask.abort(405)


@CHAT_BP.route("/topics", methods=["GET"])
@flask_login.login_required
def choose_topics() -> str:
    """Displays the page to choose favorite topics."""
    user = flask_login.current_user

    topics = app.TOPICS.get_topic_categories()

    return flask.render_template(
        "chat/topics_selection.html",
        username=user.username,
        topics=topics,
    )


@CHAT_BP.route("/topics", methods=["POST"])
@flask_login.login_required
def preferred_topics() -> Response:
    """Saves participant's favorite topics. Then redirects then to the lobby."""
    user = flask_login.current_user
    topics = flask.request.form.getlist("preferred-topic")
    topics = [topic.replace("-", " ") for topic in topics]
    username_key = redis_utils.make_username_key(user.username, user.role)
    user_key = redis_utils.redis_inst.get(username_key)

    user_id = user.user_id
    role = user.role
    if role == "1":
        redis_utils.create_rooms(user_id, topics)
    else:
        flask.abort(405)

    topics = ", ".join(topics)
    redis_utils.hmset(user_key, {"topics": topics})

    return flask.redirect(flask.url_for("chat_bp.lobby"))


@CHAT_BP.route("/lobby", methods=["GET"])
@flask_login.login_required
def lobby() -> str:
    """Displays lobby page."""
    user = flask_login.current_user
    rooms = redis_utils.get_rooms()

    if user.role == "1":
        rooms = redis_utils.get_assistant_rooms(user.user_id)

    return flask.render_template(
        "chat/lobby.html",
        user=user,
        rooms=rooms,
    )


@CHAT_BP.route("/room/leave", methods=["POST"])
@flask_login.login_required
def leave_room() -> Response:
    """Removes user from room."""
    user = flask_login.current_user

    checklist = flask.request.form.getlist("checklist")
    nb_tasks = int(flask.request.form.get("nb-tasks"))
    room_id = flask.request.form.get("room-id")
    private_room_id = flask.request.form.get("private-room-id")

    if len(checklist) == nb_tasks:
        room = redis_utils.get_room_by_id(room_id)

        role = False if user.role == "0" else True

        if role:
            redis_utils.hmset(
                private_room_id, {"assistant_checklist": json.dumps(checklist)}
            )
        else:
            redis_utils.hmset(
                private_room_id, {"client_checklist": json.dumps(checklist)}
            )

        redis_utils.remove_room(room)
        room.remove_participant(int(user.user_id), role)
        redis_utils.add_room(room)

        # Save Redis data
        redis_utils.bgsave()

        return flask.redirect(flask.url_for("chat_bp.lobby"))
    elif len(checklist) > nb_tasks:
        flask.abort(500)

    return flask.jsonify(
        {
            "msg": "You have not completed the checklist. "
            "Press OK to leave the room anyways."
        }
    )


@CHAT_BP.route("/search", methods=["POST"])
@flask_login.login_required
def search() -> Dict[str, List]:
    """Performs retrieval against Elasticsearch.

    Returns:
        Search results against desired indices.
    """
    indices = flask.request.form.getlist("indices")
    query = flask.request.form.get("query")

    # Log queries in Redis store
    private_room_id = flask.request.form.get("private_room_id")
    timestamp = flask.request.form.get("date")
    log_key = f"log:{private_room_id}"
    redis_utils.redis_inst.zadd(
        log_key,
        {json.dumps({"query": query, "indices": indices}): int(timestamp)},
    )

    data = {"products": list(), "results": list()}

    if "general" in indices:
        data["results"] = es_utils.search_trec(query, num_results=20)

    return flask.jsonify(data)


@CHAT_BP.route("/save", methods=["POST"])
@flask_login.login_required
def save_message() -> Response:
    """Saves a message to file.

    Solution to save messages in Redis in case socket.io fails.
    """
    data = flask.request.json["data"]
    id_room = (
        data["private_room_id"]
        if data["private_room_id"] != "undefined"
        else data["room_id"]
    )
    filepath = os.path.join("data/conversation_backup", f"{id_room}.txt")
    with open(filepath, "a") as file:
        file.write(f"\n{json.dumps(data)}")
    return Response(status=200)


def load_product(topic: str) -> List[Dict[str, Any]]:
    """Loads the product available for a topic.

    Args:
        topic: Topic.

    Returns:
        List of available product.
    """
    filename = f"{topic.replace(' ', '')}_items.json"
    filepath = os.path.join("data/items", filename)
    with open(filepath, "r") as file:
        products = json.load(file)
    return products
