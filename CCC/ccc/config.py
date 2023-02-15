"""Define several configuration for the application."""

import os
from os import path

import dotenv
import redis
from flask_socketio import SocketIO

basedir = path.abspath(path.dirname(__file__))
dotenv.load_dotenv(path.join(basedir, ".env"))


class BaseConfig(object):
    """Basic configuration."""

    TESTING = False
    DEBUG = False
    APP_NAME = "Flask WoZ"
    SECRET_KEY = os.environ.get("SECRET_KEY")

    socketio = SocketIO(logger=True, engineio_logger=True)

    # Configure redis
    REDIS_CHAN = "chat"
    REDIS_HOST = os.environ.get("REDIS_HOST")
    REDIS_PORT = os.environ.get("REDIS_PORT")
    redis_inst = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
    )

    SESSION_TYPE = "redis"

    # Elasticsearch
    # TREC CAsT
    ES_HOST_CAST = os.environ.get("ES_HOST_CAST")
    ES_INDEX_CAST = {
        "hostname": ES_HOST_CAST,
        "kargs": {},
        "index_name": "ms_marco_v2_kilt_wapo_new",
    }
    ES_RETRIEVER_CAST = {"fields": ["body"], "k1": 1.2, "b": 0.75}


class DevelopmentConfig(BaseConfig):
    """Configuration for development phase."""

    DEBUG = True


class TestingConfig(BaseConfig):
    """Configuration for testing the application."""

    TESTING = True
    # Configure redis
    redis_inst = redis.Redis(
        host=BaseConfig.REDIS_HOST,
        port=BaseConfig.REDIS_PORT,
        db=1,
        decode_responses=True,
    )


class ProductionConfig(BaseConfig):
    """Configuration for production release."""

    pass


def get_config(env: str) -> BaseConfig:
    """Retrieve the configuration according to development phase.

    Args:
        env: development phase (e.g., production, testing, development).

    Returns:
        Configuration corresponding to development phase.
        By default returns the configuration related to the development phase.
    """
    if env == "production":
        return ProductionConfig
    elif env == "testing":
        return TestingConfig
    return DevelopmentConfig
