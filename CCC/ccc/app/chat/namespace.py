"""Define classes to handle socket.io events associated to a namespace."""
import copy
import json
from typing import Any, Dict

import ccc.utils.redis.redis_utils as redis_utils
import flask
import flask_login
import flask_socketio
from ccc import app
from ccc.app.chat.room import RoomEncoder
from flask_socketio import Namespace


def publish(
    name: str, message: Dict, broadcast=False, room=None, namespace=None
) -> None:
    """Publishes message either with socket.io or redis pub/sub.

    Args:
        name: Type of the message.
        message: Dictionary with all information related to the type of message.
        broadcast (optional): Broadcast or not the message. Defaults to False.
        room (optional): Id of the room where to send the message. Defaults to
          None.
        namespace (optional): Namespace where to publish message. Defaults to
          None.
    """
    if room:
        flask_socketio.emit(
            name, message, room=room, broadcast=True, namespace=namespace
        )
    else:
        flask_socketio.emit(
            name, message, broadcast=broadcast, namespace=namespace
        )
    # Here is an additional publish for the redis pub/sub
    outgoing = {
        "server_id": redis_utils.SERVER_ID,
        "type": name,
        "data": message,
    }
    redis_utils.redis_inst.publish(
        redis_utils.redis_channel, json.dumps(outgoing)
    )


def escape(message: str) -> str:
    """Cleans up html from the incoming message.

    Args:
        message: Incoming message.

    Returns:
        Message without html.
    """
    escapes = {'"': "&quot;", "'": "&#39;", "<": "&lt;", ">": "&gt;"}
    message = message.replace("&", "&amp;")
    for seq, esc in escapes.items():
        message = message.replace(seq, esc)
    return message


class ChatNamespace(Namespace):
    @flask_login.login_required
    def on_connect(self) -> None:
        user = flask_login.current_user

        msg = user.__dict__
        publish("connected", msg, broadcast=True, namespace=self.namespace)

    @flask_login.login_required
    def on_disconnect(self) -> None:
        publish(
            "disconnected",
            {},
            broadcast=True,
            namespace=self.namespace,
        )

    @flask_login.login_required
    def on_server_receive(self, data: Dict) -> None:
        """Handles incoming message.

        Args:
            data: Information sent by the client through socket.io.
        """
        data["msg"] = escape(data["msg"])

        scenario = data["scenario"]
        scenario_id = scenario["id"] if scenario else None

        # The user might be set as offline if he tried to access the chat from
        # another tab, pinging by message resets the user online status.
        redis_utils.redis_inst.sadd("online_users", data["from"])

        message_string = json.dumps(data)
        room = redis_utils.get_room_by_id(data["room_id"])
        room_id = redis_utils.get_private_room_id(room, scenario_id=scenario_id)

        room_key = f"room:{room_id}"
        redis_utils.redis_inst.sadd("conversations", room_id)

        room_has_messages = bool(redis_utils.redis_inst.exists(room_key))

        if not room_has_messages:
            redis_utils.add_participants_rooms(room_id)
        redis_utils.redis_inst.zadd(
            room_key, {message_string: int(data["date"])}
        )

        publish("message", data, room=data["room_id"], namespace=self.namespace)

    @flask_login.login_required
    def on_join(self, data: Dict) -> None:
        """Participant joins the room.

        If the chat room has an history the last 15 messages are displayed.

        Args:
            data: Information sent by the client through socket.io.
        """
        flask_socketio.join_room(data["room_id"])

        scenario = data["scenario"]
        scenario_id = scenario["id"] if scenario else None

        room = redis_utils.get_room_by_id(data["room_id"])
        room_id = redis_utils.get_private_room_id(room, scenario_id)

        room_key = f"room:{room_id}"

        room_has_messages = bool(redis_utils.redis_inst.exists(room_key))

        messages = list()
        if room_has_messages:
            messages = redis_utils.get_messages(
                room_id=room_id, offset=0, size=15
            )

        if scenario:
            redis_utils.hmset(room_id, scenario)
            publish(
                "share-scenario",
                {"scenario": json.dumps(scenario)},
                room=room.room_id,
                namespace=self.namespace,
            )

        data = {"messages": messages}
        data["room_status"] = room.is_full
        publish(
            "show-history", data, room=room.room_id, namespace=self.namespace
        )

        if room.is_full:
            publish(
                "private-room-id",
                room_id,
                room=room.room_id,
                namespace=self.namespace,
            )

        publish(
            "room-status",
            {
                "is_full": room.is_full,
            },
            room=room_id,
            namespace=self.namespace,
        )

    @flask_login.login_required
    def on_leave(self, data: Dict) -> None:
        """Triggered when user leaves the chat room. Saves progress and removes
        user from room.

        Args:
            data: Information sent by the client through socket.io.
        """
        room_id = data["room_id"]
        private_room_id = data["private_room_id"]
        role = False if data["role"] == "0" else True
        user_id = int(data["user_id"])

        room = redis_utils.get_room_by_id(room_id)
        try:
            old_room = copy.deepcopy(room)

            room.remove_participant(user_id, role)
            redis_utils.remove_room(old_room)
            redis_utils.add_room(room)

            if role:
                redis_utils.hmset(
                    private_room_id, {"assistant_checklist": data["checklist"]}
                )
            else:
                redis_utils.hmset(
                    private_room_id, {"client_checklist": data["checklist"]}
                )

            publish(
                "room-status",
                {
                    "is_full": room.is_full,
                    "close": True if len(room.participants) == 1 else False,
                },
                room=room_id,
                namespace=self.namespace,
            )

            publish(
                "redirect",
                {
                    "url": flask.url_for("chat_bp.lobby"),
                    "token": private_room_id,
                },
                namespace=self.namespace,
            )
        except RuntimeError as e:
            print(e)
        redis_utils.bgsave()

    @flask_login.login_required
    def on_timer(self, data: Dict) -> None:
        """Updates countdown timer in the room and in the lobby.

        Args:
            data: Information sent by the client through socket.io.
        """
        countdown_time = data["time"]
        room_id = data["room_id"]

        publish(
            "countdown",
            {"time": countdown_time, "countdown": data["countdown"]},
            namespace=self.namespace,
            room=room_id,
        )

        publish(
            "countdown",
            {"time": countdown_time, "room_id": room_id},
            namespace=app.LOBBY_NAMESPACE,
            broadcast=True,
        )

    @flask_login.login_required
    def on_ctimeout(self, data: Dict) -> None:
        """Informs users that the conversation has finished.

        Args:
            data: Information sent by the client through socket.io.
        """
        publish(
            "chat-timeout",
            {},
            namespace=self.namespace,
            room=data["room_id"],
        )

    @flask_login.login_required
    def on_typing(self, data: Dict) -> None:
        """Informs users that a participant is typing.

        Args:
            data: Information sent by the client through socket.io.
        """
        publish(
            "is-typing",
            {"username": data["username"], "msg_length": data["length"]},
            namespace=self.namespace,
            room=data["room_id"],
        )


class LobbyNamespace(Namespace):
    @flask_login.login_required
    def on_connect(self) -> None:
        user = flask_login.current_user

        user_id = user.user_id
        redis_utils.redis_inst.sadd("online_users", user_id)

        for room in redis_utils.get_rooms():
            try:
                old_room = copy.deepcopy(room)

                role = False if user.role == "0" else True
                room.remove_participant(int(user_id), role)
                redis_utils.remove_room(old_room)
                redis_utils.add_room(room)
                publish(
                    "room-status",
                    {
                        "is_full": room.is_full,
                        "close": True if len(room.participants) == 1 else False,
                    },
                    room=room.room_id,
                    namespace=app.CHAT_NAMESPACE,
                )
            except RuntimeError as e:
                print(e)

        msg = user.__dict__
        msg["online"] = True
        msg["rooms"] = json.dumps(redis_utils.get_rooms(), cls=RoomEncoder)

        publish("connected", msg, broadcast=True, namespace=self.namespace)

    @flask_login.login_required
    def on_log_out(self) -> None:
        """Logs out a participant.

        If the participant is an assistant, their rooms are removed from
        the list displayed in the lobby.
        """
        user = flask_login.current_user

        redis_utils.redis_inst.srem("online_users", user.user_id)
        msg = user.__dict__
        msg["online"] = False

        if user.role == "1":
            redis_utils.close_rooms(user.user_id)
            msg["rooms"] = json.dumps(redis_utils.get_rooms(), cls=RoomEncoder)

        publish(
            "disconnected",
            msg,
            broadcast=True,
            namespace=self.namespace,
        )

    @flask_login.login_required
    def on_join(self, data: Dict) -> None:
        room_id = data["room_id"]
        flask_socketio.join_room(room_id)

    @flask_login.login_required
    def on_join_room(self, data: Dict) -> Any:
        """Joins chat room.

        Args:
            data: Information sent by the client through socket.io.
        """
        room_id = data["room_id"]
        role = False if data["role"] == 0 else True

        try:
            room = redis_utils.get_room_by_id(room_id)
            old_room = copy.deepcopy(room)

            room.add_participant(data["user_id"], is_assistant=role)
            redis_utils.remove_room(old_room)
            redis_utils.add_room(room)

            publish(
                "joined",
                {"rooms": json.dumps(redis_utils.get_rooms(), cls=RoomEncoder)},
                broadcast=True,
                namespace=self.namespace,
            )
            flask_socketio.join_room(room_id)

            publish(
                "redirect",
                {"url": flask.url_for("chat_bp.room", room_id=room_id)},
                namespace=self.namespace,
            )

            publish(
                "room-status",
                {"is_full": room.is_full},
                room=room_id,
                namespace=app.CHAT_NAMESPACE,
            )
        except RuntimeError as e:
            print(e)
            publish(
                "room-full",
                {"room_id": room_id},
                broadcast=False,
                namespace=self.namespace,
            )
