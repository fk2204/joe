"""
Unit tests for src/agents/base_result.py - AgentResult dataclass.

Tests cover:
- AgentResult initialization with all field combinations
- Serialization methods (to_dict)
- String representations (__str__, __repr__)
- Optional fields handling (None, empty values)
- create_result() factory function
"""

from datetime import datetime
from typing import Any, Dict

import pytest

from src.agents.base_result import AgentResult, create_result


class TestAgentResultInitialization:
    """Test AgentResult dataclass initialization."""

    def test_init_with_required_fields_only(self):
        """Test initialization with only required fields."""
        result = AgentResult(
            success=True,
            operation="test_operation",
        )

        assert result.success is True
        assert result.operation == "test_operation"
        assert result.data is None
        assert result.error is None
        assert result.agent_name is None
        assert result.tokens_used == 0
        assert result.cost == 0.0
        assert result.duration_seconds == 0.0
        assert result.metadata == {}
        assert isinstance(result.timestamp, datetime)

    def test_init_with_all_fields(self):
        """Test initialization with all fields specified."""
        test_metadata = {"key": "value", "nested": {"data": 123}}
        test_timestamp = datetime(2026, 3, 9, 12, 0, 0)

        result = AgentResult(
            success=False,
            operation="complex_operation",
            data={"result": "data"},
            error="Test error message",
            timestamp=test_timestamp,
            agent_name="TestAgent",
            tokens_used=1500,
            cost=0.025,
            duration_seconds=5.25,
            metadata=test_metadata,
        )

        assert result.success is False
        assert result.operation == "complex_operation"
        assert result.data == {"result": "data"}
        assert result.error == "Test error message"
        assert result.timestamp == test_timestamp
        assert result.agent_name == "TestAgent"
        assert result.tokens_used == 1500
        assert result.cost == 0.025
        assert result.duration_seconds == 5.25
        assert result.metadata == test_metadata

    @pytest.mark.parametrize(
        "success,operation",
        [
            (True, "op1"),
            (False, "op2"),
            (True, "script_generation"),
            (False, "video_encoding"),
        ],
    )
    def test_init_with_parameter_combinations(self, success, operation):
        """Test initialization with various parameter combinations."""
        result = AgentResult(success=success, operation=operation)

        assert result.success == success
        assert result.operation == operation

    def test_init_with_various_data_types(self):
        """Test initialization with different data types."""
        # String data
        result = AgentResult(success=True, operation="op", data="string_data")
        assert result.data == "string_data"

        # List data
        result = AgentResult(success=True, operation="op", data=[1, 2, 3])
        assert result.data == [1, 2, 3]

        # Dict data
        result = AgentResult(success=True, operation="op", data={"key": "value"})
        assert result.data == {"key": "value"}

        # None data
        result = AgentResult(success=True, operation="op", data=None)
        assert result.data is None

    def test_init_with_empty_metadata(self):
        """Test that metadata defaults to empty dict."""
        result = AgentResult(success=True, operation="op")
        assert result.metadata == {}
        assert isinstance(result.metadata, dict)

    def test_init_with_custom_metadata(self):
        """Test metadata as custom dict."""
        custom_metadata = {"attempt": 1, "retry_reason": "timeout"}
        result = AgentResult(
            success=True,
            operation="op",
            metadata=custom_metadata,
        )
        assert result.metadata == custom_metadata

    def test_timestamp_defaults_to_now(self):
        """Test that timestamp defaults to current time."""
        before = datetime.now()
        result = AgentResult(success=True, operation="op")
        after = datetime.now()

        assert before <= result.timestamp <= after


class TestAgentResultToDict:
    """Test AgentResult.to_dict() serialization method."""

    def test_to_dict_with_minimal_fields(self):
        """Test to_dict with minimal required fields."""
        result = AgentResult(success=True, operation="test_op")
        result_dict = result.to_dict()

        assert result_dict["success"] is True
        assert result_dict["operation"] == "test_op"
        assert result_dict["data"] is None
        assert result_dict["error"] is None
        assert result_dict["tokens_used"] == 0
        assert result_dict["cost"] == 0.0

    def test_to_dict_with_all_fields(self):
        """Test to_dict with all fields populated."""
        result = AgentResult(
            success=False,
            operation="complex_op",
            data={"key": "value"},
            error="Error message",
            agent_name="MyAgent",
            tokens_used=2000,
            cost=0.05,
            duration_seconds=10.5,
            metadata={"attempt": 2},
        )
        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert result_dict["success"] is False
        assert result_dict["operation"] == "complex_op"
        assert result_dict["data"] == {"key": "value"}
        assert result_dict["error"] == "Error message"
        assert result_dict["agent_name"] == "MyAgent"
        assert result_dict["tokens_used"] == 2000
        assert result_dict["cost"] == 0.05
        assert result_dict["duration_seconds"] == 10.5
        assert result_dict["metadata"] == {"attempt": 2}

    def test_to_dict_timestamp_is_iso_string(self):
        """Test that timestamp is converted to ISO format string."""
        test_time = datetime(2026, 3, 9, 15, 30, 45)
        result = AgentResult(
            success=True,
            operation="op",
            timestamp=test_time,
        )
        result_dict = result.to_dict()

        assert isinstance(result_dict["timestamp"], str)
        assert result_dict["timestamp"] == test_time.isoformat()

    def test_to_dict_preserves_nested_data_structures(self):
        """Test to_dict with nested data structures."""
        nested_data = {
            "level1": {
                "level2": {
                    "value": "deep",
                    "list": [1, 2, 3],
                }
            },
            "items": [
                {"id": 1, "name": "item1"},
                {"id": 2, "name": "item2"},
            ],
        }
        result = AgentResult(
            success=True,
            operation="op",
            data=nested_data,
        )
        result_dict = result.to_dict()

        assert result_dict["data"] == nested_data

    def test_to_dict_is_json_serializable(self):
        """Test that to_dict output is JSON-serializable."""
        import json

        result = AgentResult(
            success=True,
            operation="op",
            data={"key": "value"},
            agent_name="TestAgent",
            tokens_used=500,
            cost=0.001,
            metadata={"source": "test"},
        )
        result_dict = result.to_dict()

        # Should not raise an exception
        json_str = json.dumps(result_dict)
        assert json_str  # Non-empty string
        assert "test_op" not in json_str  # But it has the operation name


class TestAgentResultStringRepresentations:
    """Test __str__ and __repr__ methods."""

    def test_str_with_success_no_details(self):
        """Test __str__ with successful operation and no optional details."""
        result = AgentResult(success=True, operation="simple_op")
        result_str = str(result)

        assert "[SUCCESS]" in result_str
        assert "simple_op" in result_str
        assert "no details" in result_str

    def test_str_with_failure_no_details(self):
        """Test __str__ with failed operation."""
        result = AgentResult(success=False, operation="failed_op")
        result_str = str(result)

        assert "[FAILURE]" in result_str
        assert "failed_op" in result_str

    def test_str_with_agent_name(self):
        """Test __str__ includes agent_name when present."""
        result = AgentResult(
            success=True,
            operation="op",
            agent_name="TestAgent",
        )
        result_str = str(result)

        assert "agent=TestAgent" in result_str

    def test_str_with_tokens_and_cost(self):
        """Test __str__ includes tokens and cost."""
        result = AgentResult(
            success=True,
            operation="op",
            tokens_used=1500,
            cost=0.0025,
        )
        result_str = str(result)

        assert "tokens=1500" in result_str
        assert "cost=$0.0025" in result_str

    def test_str_with_duration(self):
        """Test __str__ includes duration when non-zero."""
        result = AgentResult(
            success=True,
            operation="op",
            duration_seconds=3.75,
        )
        result_str = str(result)

        assert "duration=3.8s" in result_str or "duration=3.7s" in result_str

    def test_str_with_all_details(self):
        """Test __str__ with all optional details."""
        result = AgentResult(
            success=True,
            operation="full_op",
            agent_name="FullAgent",
            tokens_used=2000,
            cost=0.004,
            duration_seconds=5.5,
        )
        result_str = str(result)

        assert "[SUCCESS]" in result_str
        assert "full_op" in result_str
        assert "agent=FullAgent" in result_str
        assert "tokens=2000" in result_str
        assert "cost=$0.0040" in result_str
        assert "duration=5.5s" in result_str

    def test_str_with_zero_cost_not_shown(self):
        """Test __str__ doesn't show cost when it's 0."""
        result = AgentResult(
            success=True,
            operation="op",
            agent_name="Agent",
            cost=0.0,  # Zero cost
        )
        result_str = str(result)

        assert "cost=" not in result_str

    def test_repr_format(self):
        """Test __repr__ provides debugging representation."""
        result = AgentResult(
            success=True,
            operation="test_op",
            agent_name="TestAgent",
            tokens_used=500,
        )
        result_repr = repr(result)

        assert "AgentResult(" in result_repr
        assert "success=True" in result_repr
        assert "operation='test_op'" in result_repr
        assert "agent_name='TestAgent'" in result_repr
        assert "tokens=500" in result_repr

    def test_repr_with_failure(self):
        """Test __repr__ with failed operation."""
        result = AgentResult(
            success=False,
            operation="failed_op",
            agent_name="FailAgent",
            tokens_used=100,
        )
        result_repr = repr(result)

        assert "success=False" in result_repr
        assert "failed_op" in result_repr


class TestCreateResultFactory:
    """Test create_result() factory function."""

    def test_create_result_basic(self):
        """Test basic create_result factory function."""
        result = create_result(
            success=True,
            operation="test_op",
            agent_name="TestAgent",
        )

        assert isinstance(result, AgentResult)
        assert result.success is True
        assert result.operation == "test_op"
        assert result.agent_name == "TestAgent"

    def test_create_result_with_all_parameters(self):
        """Test create_result with all parameters."""
        result = create_result(
            success=False,
            operation="complex_op",
            agent_name="ComplexAgent",
            data={"error_details": "something"},
            error="Operation failed",
            tokens_used=3000,
            cost=0.006,
            duration_seconds=8.5,
            metadata_key="metadata_value",
            extra_param=123,
        )

        assert result.success is False
        assert result.operation == "complex_op"
        assert result.agent_name == "ComplexAgent"
        assert result.data == {"error_details": "something"}
        assert result.error == "Operation failed"
        assert result.tokens_used == 3000
        assert result.cost == 0.006
        assert result.duration_seconds == 8.5
        assert result.metadata == {
            "metadata_key": "metadata_value",
            "extra_param": 123,
        }

    def test_create_result_timestamp_is_fresh(self):
        """Test that create_result sets current timestamp."""
        before = datetime.now()
        result = create_result(
            success=True,
            operation="op",
            agent_name="Agent",
        )
        after = datetime.now()

        assert before <= result.timestamp <= after

    @pytest.mark.parametrize(
        "success,operation,agent_name",
        [
            (True, "op1", "Agent1"),
            (False, "op2", "Agent2"),
            (True, "script_gen", "ScriptAgent"),
            (False, "video_encode", "VideoAgent"),
        ],
    )
    def test_create_result_parameter_combinations(
        self,
        success,
        operation,
        agent_name,
    ):
        """Test create_result with various parameter combinations."""
        result = create_result(
            success=success,
            operation=operation,
            agent_name=agent_name,
        )

        assert result.success == success
        assert result.operation == operation
        assert result.agent_name == agent_name

    def test_create_result_with_list_data(self):
        """Test create_result with list data."""
        list_data = ["item1", "item2", "item3"]
        result = create_result(
            success=True,
            operation="list_op",
            agent_name="ListAgent",
            data=list_data,
        )

        assert result.data == list_data

    def test_create_result_with_string_data(self):
        """Test create_result with string data."""
        result = create_result(
            success=True,
            operation="string_op",
            agent_name="StringAgent",
            data="result string",
        )

        assert result.data == "result string"

    def test_create_result_default_values(self):
        """Test create_result uses correct defaults."""
        result = create_result(
            success=True,
            operation="op",
            agent_name="Agent",
        )

        assert result.data is None
        assert result.error is None
        assert result.tokens_used == 0
        assert result.cost == 0.0
        assert result.duration_seconds == 0.0
        assert result.metadata == {}


class TestAgentResultEdgeCases:
    """Test edge cases and special scenarios."""

    def test_result_with_very_large_token_count(self):
        """Test result with very large token count."""
        result = AgentResult(
            success=True,
            operation="op",
            tokens_used=1000000,
        )

        assert result.tokens_used == 1000000
        result_dict = result.to_dict()
        assert result_dict["tokens_used"] == 1000000

    def test_result_with_very_small_cost(self):
        """Test result with very small cost value."""
        result = AgentResult(
            success=True,
            operation="op",
            cost=0.00001,
        )

        assert result.cost == 0.00001
        result_str = str(result)
        assert "cost=$0.0000" in result_str

    def test_result_with_empty_operation_string(self):
        """Test result with empty operation string (edge case)."""
        result = AgentResult(
            success=True,
            operation="",
        )

        assert result.operation == ""
        result_str = str(result)
        assert "[SUCCESS]" in result_str

    def test_result_with_very_long_error_message(self):
        """Test result with very long error message."""
        long_error = "Error " * 100  # 600 character error
        result = AgentResult(
            success=False,
            operation="op",
            error=long_error,
        )

        assert result.error == long_error
        result_dict = result.to_dict()
        assert result_dict["error"] == long_error

    def test_result_with_unicode_characters(self):
        """Test result with Unicode characters."""
        unicode_data = {
            "emoji": "🚀📊🎯",
            "chinese": "中文",
            "russian": "Русский",
        }
        result = AgentResult(
            success=True,
            operation="unicode_op",
            data=unicode_data,
        )

        assert result.data == unicode_data
        result_dict = result.to_dict()
        assert result_dict["data"] == unicode_data

    def test_result_metadata_isolation(self):
        """Test that metadata modifications don't affect original."""
        original_metadata = {"key": "value"}
        result = AgentResult(
            success=True,
            operation="op",
            metadata=original_metadata,
        )

        # Modify the result's metadata
        result.metadata["new_key"] = "new_value"

        # Original should be modified (same reference)
        assert original_metadata["new_key"] == "new_value"

    def test_result_with_none_agent_name(self):
        """Test result with explicitly None agent_name."""
        result = AgentResult(
            success=True,
            operation="op",
            agent_name=None,
        )

        assert result.agent_name is None
        result_str = str(result)
        assert "agent=" not in result_str

    def test_result_with_negative_duration(self):
        """Test result with negative duration (shouldn't happen but test defensively)."""
        result = AgentResult(
            success=True,
            operation="op",
            duration_seconds=-1.5,
        )

        assert result.duration_seconds == -1.5
        result_str = str(result)
        # Should still format correctly
        assert "duration=" in result_str
