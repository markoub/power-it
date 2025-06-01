"""Test utilities module for PowerIt backend tests."""

from .vcr_base import BaseVCR
from .env_manager import EnvironmentManager
from .module_manager import ModuleManager
from .mock_factories import MockFactory
from .helpers import (
    wait_for_condition,
    assert_api_error,
    create_test_presentation,
    assert_valid_research_data,
    assert_valid_slide_presentation,
    assert_file_exists_and_valid,
    compare_slides,
)

__all__ = [
    "BaseVCR",
    "EnvironmentManager",
    "ModuleManager",
    "MockFactory",
    "wait_for_condition",
    "assert_api_error",
    "create_test_presentation",
    "assert_valid_research_data",
    "assert_valid_slide_presentation",
    "assert_file_exists_and_valid",
    "compare_slides",
]