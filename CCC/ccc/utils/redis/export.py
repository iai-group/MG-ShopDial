"""Export data from Redis store to file."""

import argparse
import ast
import html
import json
from typing import Any, Dict

from redis import Redis

_OUTPUT_DIR = "data/conversations.json"
_REDIS_HOST = "localhost"
_REDIS_PORT = 6379


def export_to_json(redis_inst: Redis, filepath: str) -> None:
    """Exports conversations with metadata to JSON file.

    Args:
        redis_inst: Redis instance to use.
        filepath: Output JSON file.
    """
    conversations = list()

    conversation_ids = redis_inst.smembers("conversations")

    for conv_id in conversation_ids:
        conv = get_conversation(conv_id, redis_inst)
        conversations.append(conv)

    with open(filepath, "w") as output_file:
        output_file.write(json.dumps(conversations, indent=4))


def get_conversation(id: str, redis_inst: Redis) -> Dict[str, Any]:
    """Retrieves all information related to a conversation.

    Args:
        id: Conversation id.
        redis_inst: Redis instance to use.

    Returns:
        Dictionary representing a conversation with metadata and messages.
    """
    conversation = {"id": id}

    # Retrieve conversation metadata (e.g., task description, search logs, etc.)
    metadata = redis_inst.hgetall(id)
    metadata["client_checklist"] = ast.literal_eval(
        metadata.get("client_checklist", "[]")
    )
    metadata["assistant_checklist"] = ast.literal_eval(
        metadata.get("assistant_checklist", "[]")
    )
    search_logs = {
        "search_logs": [
            json.loads(q) for q in redis_inst.zrange(f"log:{id}", 0, -1)
        ]
    }
    metadata.update(search_logs)
    conversation["metadata"] = metadata

    # Retrieve messages
    role_mapping = dict()
    for user_id in id.split(":")[1:]:
        user = redis_inst.hgetall(f"user:{user_id}")
        role_mapping[user["username"]] = (
            "Assistant" if user["role"] == "1" else "Client"
        )
    messages = list(
        map(lambda x: json.loads(x), redis_inst.zrange(f"room:{id}", 0, -1))
    )
    messages = [
        parse_message(i, m, role_mapping) for i, m in enumerate(messages)
    ]
    conversation["utterances"] = messages
    return conversation


def parse_message(
    utterance_id: int, message: Dict[str, str], role_mapping: Dict[str, str]
) -> Dict[str, str]:
    """Parses a message extracted from Redis store.

    Args:
        utterance_id: Position of the utterance in the conversation.
        message: Message to parse.
        role_mapping: Map username to role.

    Returns:
        Dictionary with information related to the utterance.
    """
    return {
        "utterance_id": utterance_id + 1,
        "participant": role_mapping[message["from"]]
        if message["from"] in role_mapping
        else message["from"],
        "utterance": html.unescape(message["msg"]),
    }


def parse_cmdline_arguments() -> argparse.Namespace:
    """Defines accepted arguments and returns the parsed values.

    Returns:
        Object with a property for each argument.
    """
    parser = argparse.ArgumentParser(prog="export.py")
    parser.add_argument(
        "--output_file",
        type=str,
        default=_OUTPUT_DIR,
        help="The path to the output JSON file for conversations.",
    )
    parser.add_argument(
        "--redis_host",
        type=str,
        default=_REDIS_HOST,
        help="Redis hostname.",
    )
    parser.add_argument(
        "--redis_port",
        type=int,
        default=_REDIS_PORT,
        help="Redis port.",
    )
    return parser.parse_args()


def main(args):
    """Exports conversations to JSON file.

    Args:
        args: Arguments.
    """
    redis_inst = Redis(
        host=args.redis_host, port=args.redis_port, db=0, decode_responses=True
    )

    export_to_json(redis_inst, args.output_file)


if __name__ == "__main__":
    args = parse_cmdline_arguments()
    main(args)
