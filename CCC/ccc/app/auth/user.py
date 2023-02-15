"""Define the User class for Flask Login."""


import json
from typing import Any

import bcrypt
from ccc.utils.redis import redis_utils
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id: int, username: str, name: str, role: int) -> None:
        """Creates a user and add it to the Redis cache.

        Args:
            id: Id.
            username: Username.
            name: Name.
            role: Whether or not the user is a shopping assistant.
        """
        self.user_id = id
        self.username = username
        self.name = name
        self.role = role
        self.username_key = redis_utils.make_username_key(username, role)

    def __str__(self) -> str:
        return json.dumps(
            {
                "user_id": self.user_id,
                "username": self.username,
                "role": self.role,
                "username_key": self.username_key,
            },
            ensure_ascii=False,
        )

    def get_id(self):
        return self.username_key

    def get_user_id(self):
        return self.user_id

    @classmethod
    def get_by_key(cls, key: str) -> Any:
        """Gets user with username key.

        Args:
            key: Redis username key.

        Returns:
            User associated with key.
        """
        user_key = redis_utils.redis_inst.get(key)

        if user_key is not None:
            user = redis_utils.hmget(user_key, ["username", "name", "role"])
            user["id"] = user_key.split(":")[-1]
            return cls(**user)
        return None

    @classmethod
    def register(
        cls, name: str, username: str, password: str, role: int
    ) -> bool:
        """Registers a user.

        Args:
            name: Name.
            username: Username.
            password: Password.
            role: Whether or not the user is a shopping assistant.

        Returns:
            Whether or not a user was registered.
        """
        username_key = redis_utils.make_username_key(username, role)
        user_exists = redis_utils.redis_inst.exists(username_key)
        if not user_exists:
            redis_utils.create_user(name, username, password, role)
            return True
        else:
            return False

    @staticmethod
    def login_valid(password: str, username_key: str) -> bool:
        """Verifies user's credentials.

        Args:
            password: Password.
            username_key: Redis username key.

        Returns:
            Whether or not the credentials are correct.
        """
        user_key = redis_utils.redis_inst.get(username_key)
        data = redis_utils.redis_inst.hgetall(user_key)
        data["password"] = data["password"].encode("utf-8")
        hash_password = bcrypt.hashpw(
            password.encode("utf-8"), data["password"]
        )
        if hash_password == data["password"]:
            return True
        return False
