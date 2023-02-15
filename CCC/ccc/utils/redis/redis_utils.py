"""Utilities functions to interact with Redis cache.

Based on the example from Redis.
https://github.com/redis-developer/basic-redis-chat-app-demo-python/"""

import json
import random
from typing import Any, Dict, List, Optional, Union

import bcrypt
import ccc.config as config
from ccc.app.chat.room import Room

SERVER_ID = random.uniform(0, 322321)


def init_redis(env: str) -> None:
    """Initializes the Redis cache regarding the environment."""
    global redis_inst
    global redis_channel

    app_config = config.get_config(env)
    # TODO refactor Config to create Redis instance here.
    redis_inst = app_config.redis_inst
    redis_channel = app_config.REDIS_CHAN

    total_users_exist = redis_inst.exists("total_users")
    if not total_users_exist:
        # If there is no user in the cache set up the total to 0.
        redis_inst.set("total_users", 0)

    # Store passphrase to access Admin dashboard
    redis_inst.set("admin_passphrase", "passphrase")


def get_admin_passphrase() -> str:
    """Retrieves passphrase to access Admin dashboard.

    Returns:
        Passphrase.
    """
    return redis_inst.get("admin_passphrase")


def make_username_key(username: str, role: int) -> str:
    """Creates a key to retrieve user in cache.

    Args:
        username: Username.
        role: Whether or not the user is the assistant.

    Returns:
        Redis key.
    """
    key = username + str(role)
    return f"username:{key}"


def user_exists(username_key: str) -> bool:
    """Checks if the user is already in the Redis cache.

    Args:
        username_key: Key associated to the user.

    Returns:
        Whether the key is in the cache.
    """
    return redis_inst.exists(username_key)


def get_online_users() -> List[Dict]:
    """Retrieves the list of online users.

    Returns:
        List of online users with their username and role.
    """
    online_ids = redis_inst.smembers("online_users")
    online_users = list()
    for id in online_ids:
        user = hmget(f"user:{id}", ["username", "role"])
        online_users.append(user)
    return online_users


def create_user(name: str, username: str, password: str, role: int) -> Dict:
    """Creates a user and add it to the Redis cache.

    Args:
        name: Name.
        username: Username.
        password: Password.
        role: Whether or not the user is an assistant.

    Returns:
        Dictionary with the id and username of the user created.
    """
    username_key = make_username_key(username, role)
    hashed_password = bcrypt.hashpw(
        str(password).encode("utf-8"), bcrypt.gensalt(10)
    )
    next_id = redis_inst.incr("total_users")
    user_key = f"user:{next_id}"
    redis_inst.set(username_key, user_key)
    hmset(
        user_key,
        {
            "name": name,
            "username": username,
            "password": hashed_password,
            "role": role,
        },
    )
    return {"id": next_id, "username": username, "role": role}


def get_messages(room_id="1:2", offset=0, size=50) -> List:
    """Fetches messages from a specific room if it exists.

    Args:
        room_id (optional): Id of the room. Defaults room 1:2.
        offset (optional): Starting offset to retrieve the messages. Defaults
          is 0.
        size (optional): Number of messages to retrieve. Defaults is 50
          messages.

    Returns:
        List of messages from the specific room.
    """
    room_key = f"room:{room_id}"
    room_exists = redis_inst.exists(room_key)
    if not room_exists:
        return []
    else:
        values = redis_inst.zrange(room_key, offset, offset + size)
        return list(map(lambda x: json.loads(x), values))


def hmget(key: str, fields: List[str]) -> Dict:
    """Gets the values associated with the specified fields in the hash
    stored at key.

    Args:
        key: Name of key.
        fields: List of fields to retrieve.

    Returns:
        Dictionary of values associated to the fields queried.
    """
    result = redis_inst.hmget(key, fields)
    return dict(zip(fields, list(map(lambda x: x, result))))


def hmset(key: str, mapping: Dict) -> List:
    """Adds/Updates values associated with the specified fields in the hash
    stored at key.

    Args:
        key: Name of key.
        mapping: Dictionary with corresponding keys and values to set.
    """
    redis_inst.hmset(key, mapping)


def bgsave() -> Any:
    """Saves Redis data to disk asynchronously."""
    return redis_inst.bgsave()


def get_private_room_id(room: Room, scenario_id: Optional[int] = None) -> str:
    """Creates id for a private room between participants currently in the room.

    Args:
        room: Chat room.
        scenario_id: Scenario id.

    Returns:
        Id of the private between the participants in the room.
    """
    split = room.room_id.split(":")
    assistant_id = int(split[-1])
    topic = split[0].replace(" ", "")

    private_room_id = (
        f"{topic}:{scenario_id}:{assistant_id}"
        if scenario_id
        else f"{topic}:{assistant_id}"
    )
    room.participants.sort()

    for id in room.participants:
        if assistant_id == id:
            continue
        private_room_id += f":{id}"
    return private_room_id


def add_participants_rooms(room_id: str) -> None:
    """Adds the private room to participants' record.

    Args:
        room_id: Id of the chatroom.

    Raises:
        RuntimeError: if the private does not have at least 2 participants.
    """
    split = room_id.split(":")

    if len(split) < 3:
        raise RuntimeError("The private room cannot have only one participant.")

    for id in split[1:]:
        redis_inst.sadd(f"user:{id}:rooms", room_id)


def create_rooms(assistant_id: int, topics: List[str]) -> None:
    """Creates a room for each favorite topics of an assistant. Stores rooms in
    Redis.

    Args:
        assistant_id: Id of the assistant.
        topics: List of assistant's favorite topics.
    """
    for topic in topics:
        id = f"{topic}:{assistant_id}"
        room = Room(id, max_user=2, topic=topic)
        redis_inst.sadd("rooms", room.__str__())


def close_rooms(assistant_id: str) -> None:
    """Removes rooms associated with an assistant.

    Args:
        assistant_id: Id of the assistant.
    """
    rooms = get_rooms()
    for room in rooms:
        id = room.room_id.split(":")[1]
        if id == assistant_id:
            redis_inst.srem("rooms", room.__str__())


def get_assistant_rooms(assistant_id: str) -> List[Room]:
    """Returns list of assistant's rooms."""
    rooms = get_rooms()
    assistant_rooms = list()
    for room in rooms:
        id = room.room_id.split(":")[1]
        if id == assistant_id:
            assistant_rooms.append(room)
    return assistant_rooms


def parse_room(room_repr: str) -> Room:
    """Parses room retrieved from redis store.

    Args:
        room_repr: String representation of the room.
    """
    room = json.loads(room_repr)
    return Room(
        room["room_id"],
        participants=room["participants"],
        max_user=room["max_user"],
        has_assistant=room["has_assistant"],
        topic=room["topic"],
    )


def get_rooms() -> List[Room]:
    """Retrieves rooms from the Redis store."""
    rooms = redis_inst.smembers("rooms")
    rooms = list(map(lambda x: parse_room(x), rooms))
    return rooms


def get_room_by_id(room_id: str) -> Union[Room, None]:
    """Returns the room corresponding to id."""
    rooms = get_rooms()
    for room in rooms:
        if room.room_id == room_id:
            return room
    return None


def remove_room(room: Room) -> None:
    """Removes room from Redis store."""
    redis_inst.srem("rooms", room.__str__())


def add_room(room: Room) -> None:
    """Adds room to Redis store."""
    redis_inst.sadd("rooms", room.__str__())


def retrieve_conversations() -> List[str]:
    """Retrieves hash of conversations.

    Returns:
        List of private room ids.
    """
    return redis_inst.smembers("conversations")
