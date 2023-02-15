"""Class to represent a room which accepts a limited number of participants."""

import json
from typing import List, Optional


class RoomEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.__dict__


class Room:
    def __init__(
        self,
        room_id: str,
        participants: List[int] = [],
        max_user: int = 2,
        has_assistant: bool = False,
        topic: Optional[str] = None,
    ) -> None:
        """Initializes chatroom.

        Args:
            room_id: Room id.
            participants (optional): Ids of the participant in the room.
              Defaults no participants in the room.
            max_user (optional): Maximum number of participants in the room.
              Defaults the room only accepts 2 participants.
            has_assistant (optional): Whether of not an assistant is in the room.
              Defaults to False.
            topic: topic of the room. Defaults to None.
        """
        self.room_id = room_id
        self.participants = participants
        self.number_user = len(self.participants)
        self.max_user = max_user
        self.has_assistant = has_assistant
        self.is_full = self.room_status()
        self.topic = topic

    def __iter__(self):
        yield from {
            "room_id": self.room_id,
            "participants": self.participants,
            "number_user": self.number_user,
            "max_user": self.max_user,
            "has_assistant": self.has_assistant,
            "is_full": self.is_full,
            "topic": self.topic,
        }.items()

    def __str__(self):
        return json.dumps(dict(self), ensure_ascii=False)

    def __repr__(self):
        return self.__str__()

    def room_status(self) -> bool:
        """Checks is the room is full."""
        if self.number_user < self.max_user:
            return False
        return True

    def add_participant(
        self, participant: int, is_assistant: bool = False
    ) -> None:
        """Adds a participant to the room if possible.

        Args:
            participant: Id of the participant.
            is_assistant: Whether or not the participant is aa assistant.
              Defaults participant is a user.

        Raises:
            RuntimeError: if the room is full.
        """
        if not self.is_full:
            if is_assistant and self.has_assistant:
                raise RuntimeError("An assistant is already in the room.")

            if (
                not is_assistant
                and not self.has_assistant
                and self.number_user >= (self.max_user - 1)
            ):
                # If room doesn't have an assistant keep last space for them.
                raise RuntimeError("Cannot add more participants to this room.")

            self.participants.append(participant)
            self.number_user += 1
            self.is_full = self.room_status()
            self.has_assistant = is_assistant or self.has_assistant
        else:
            raise RuntimeError("Cannot add more participants to this room.")

    def remove_participant(
        self, participant: int, is_assistant: bool = False
    ) -> None:
        """Removes a participant to the room if possible.

        Args:
            participant: Id of the participant.
            is_assistant: Whether or not the participant is an assistant.
              Defaults participant is a user.

        Raises:
            RuntimeError: The participant is not in the room.
        """
        try:
            self.participants.remove(participant)
            self.number_user -= 1
            self.is_full = self.room_status()
            if is_assistant:
                self.has_assistant = False
        except Exception:
            raise RuntimeError(
                f"The participant {participant} is not present in this room."
            )
