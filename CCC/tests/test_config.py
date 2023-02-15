"""Test configuration for FLask application."""

import pytest
import ccc.config as conf
from ccc.config import (
    BaseConfig,
    DevelopmentConfig,
    ProductionConfig,
    TestingConfig,
)


@pytest.mark.parametrize(
    "env, config",
    [
        ("testing", TestingConfig),
        ("production", ProductionConfig),
        ("development", DevelopmentConfig),
        ("unknown", DevelopmentConfig),
    ],
)
def test_get_config(env: str, config: BaseConfig) -> None:
    config_ = conf.get_config(env)
    assert config_ == config
