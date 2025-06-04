import pytest
import asyncio
from unittest.mock import Mock, patch
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from temporal_workflows import (
    ReverseStringWorkflow,
    reverse_string_activity,
    validate_input_activity,
    ReverseResult
)

class TestReverseStringActivity:
    """Test cases for the reverse string activity"""
    
    @pytest.mark.asyncio
    async def test_reverse_string_simple(self):
        """Test basic string reversal"""
        result = await reverse_string_activity("hello")
        
        assert isinstance(result, ReverseResult)
        assert result.original_text == "hello"
        assert result.reversed_text == "olleh"
        assert result.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_reverse_string_empty(self):
        """Test reversing empty string"""
        result = await reverse_string_activity("")
        
        assert result.original_text == ""
        assert result.reversed_text == ""
        assert result.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_reverse_string_special_chars(self):
        """Test reversing string with special characters"""
        text = "Hello, World! 123"
        result = await reverse_string_activity(text)
        
        assert result.original_text == text
        assert result.reversed_text == "321 !dlroW ,olleH"
        assert result.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_reverse_string_unicode(self):
        """Test reversing string with Unicode characters"""
        text = "Hello 世界! 🌍"
        result = await reverse_string_activity(text)
        
        assert result.original_text == text
        assert result.reversed_text == "🌍 !界世 olleH"
        assert result.processing_time_ms > 0

class TestValidateInputActivity:
    """Test cases for the input validation activity"""
    
    @pytest.mark.asyncio
    async def test_validate_normal_input(self):
        """Test validation of normal input"""
        result = await validate_input_activity("Hello World")
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_empty_input(self):
        """Test validation fails for empty input"""
        with pytest.raises(ValueError, match="Input text cannot be empty"):
            await validate_input_activity("")
    
    @pytest.mark.asyncio
    async def test_validate_whitespace_only(self):
        """Test validation fails for whitespace-only input"""
        with pytest.raises(ValueError, match="Input text cannot be empty"):
            await validate_input_activity("   ")
    
    @pytest.mark.asyncio
    async def test_validate_too_long_input(self):
        """Test validation fails for input that's too long"""
        long_text = "a" * 10001  # 10,001 characters
        with pytest.raises(ValueError, match="Input text too long"):
            await validate_input_activity(long_text)
    
    @pytest.mark.asyncio
    async def test_validate_max_length_input(self):
        """Test validation passes for input at max length"""
        max_length_text = "a" * 10000  # Exactly 10,000 characters
        result = await validate_input_activity(max_length_text)
        assert result is True

class TestReverseStringWorkflow:
    """Test cases for the reverse string workflow"""
    
    @pytest.mark.asyncio
    async def test_workflow_success(self):
        """Test successful workflow execution"""
        async with WorkflowEnvironment() as env:
            # Create worker with workflow and activities
            worker = Worker(
                env.client,
                task_queue="test-queue",
                workflows=[ReverseStringWorkflow],
                activities=[reverse_string_activity, validate_input_activity],
            )
            
            async with worker:
                # Execute workflow
                result = await env.client.execute_workflow(
                    ReverseStringWorkflow.run,
                    "hello",
                    id="test-workflow",
                    task_queue="test-queue",
                )
                
                assert result["success"] is True
                assert result["original_text"] == "hello"
                assert result["reversed_text"] == "olleh"
                assert result["processing_time_ms"] > 0
                assert result["workflow_id"] == "test-workflow"
                assert result["error"] is None
    
    @pytest.mark.asyncio
    async def test_workflow_validation_failure(self):
        """Test workflow with validation failure"""
        async with WorkflowEnvironment() as env:
            worker = Worker(
                env.client,
                task_queue="test-queue",
                workflows=[ReverseStringWorkflow],
                activities=[reverse_string_activity, validate_input_activity],
            )
            
            async with worker:
                # Execute workflow with empty input
                result = await env.client.execute_workflow(
                    ReverseStringWorkflow.run,
                    "",
                    id="test-workflow-fail",
                    task_queue="test-queue",
                )
                
                assert result["success"] is False
                assert result["original_text"] == ""
                assert result["reversed_text"] == ""
                assert result["processing_time_ms"] == 0
                assert result["workflow_id"] == "test-workflow-fail"
                assert "Input text cannot be empty" in result["error"]
    
    @pytest.mark.asyncio
    async def test_workflow_complex_input(self):
        """Test workflow with complex input"""
        async with WorkflowEnvironment() as env:
            worker = Worker(
                env.client,
                task_queue="test-queue",
                workflows=[ReverseStringWorkflow],
                activities=[reverse_string_activity, validate_input_activity],
            )
            
            async with worker:
                complex_text = "The quick brown fox jumps over the lazy dog! 🦊"
                expected_reversed = "🦊 !god yzal eht revo spmuj xof nworb kciuq ehT"
                
                result = await env.client.execute_workflow(
                    ReverseStringWorkflow.run,
                    complex_text,
                    id="test-workflow-complex",
                    task_queue="test-queue",
                )
                
                assert result["success"] is True
                assert result["original_text"] == complex_text
                assert result["reversed_text"] == expected_reversed
                assert result["processing_time_ms"] > 0

class TestWorkflowEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.mark.asyncio
    async def test_very_long_valid_input(self):
        """Test workflow with maximum valid input length"""
        async with WorkflowEnvironment() as env:
            worker = Worker(
                env.client,
                task_queue="test-queue",
                workflows=[ReverseStringWorkflow],
                activities=[reverse_string_activity, validate_input_activity],
            )
            
            async with worker:
                # Create text at maximum allowed length (10,000 chars)
                long_text = "a" * 9995 + "hello"  # 10,000 total
                expected_reversed = "olleh" + "a" * 9995
                
                result = await env.client.execute_workflow(
                    ReverseStringWorkflow.run,
                    long_text,
                    id="test-workflow-long",
                    task_queue="test-queue",
                )
                
                assert result["success"] is True
                assert result["original_text"] == long_text
                assert result["reversed_text"] == expected_reversed
                assert len(result["reversed_text"]) == 10000
    
    @pytest.mark.asyncio
    async def test_single_character(self):
        """Test workflow with single character input"""
        async with WorkflowEnvironment() as env:
            worker = Worker(
                env.client,
                task_queue="test-queue",
                workflows=[ReverseStringWorkflow],
                activities=[reverse_string_activity, validate_input_activity],
            )
            
            async with worker:
                result = await env.client.execute_workflow(
                    ReverseStringWorkflow.run,
                    "A",
                    id="test-workflow-single",
                    task_queue="test-queue",
                )
                
                assert result["success"] is True
                assert result["original_text"] == "A"
                assert result["reversed_text"] == "A"
    
    @pytest.mark.asyncio
    async def test_palindrome(self):
        """Test workflow with palindrome input"""
        async with WorkflowEnvironment() as env:
            worker = Worker(
                env.client,
                task_queue="test-queue",
                workflows=[ReverseStringWorkflow],
                activities=[reverse_string_activity, validate_input_activity],
            )
            
            async with worker:
                palindrome = "racecar"
                result = await env.client.execute_workflow(
                    ReverseStringWorkflow.run,
                    palindrome,
                    id="test-workflow-palindrome",
                    task_queue="test-queue",
                )
                
                assert result["success"] is True
                assert result["original_text"] == palindrome
                assert result["reversed_text"] == palindrome  # Should be the same

# Test fixtures and utilities
@pytest.fixture
def sample_texts():
    """Fixture providing sample texts for testing"""
    return {
        "simple": "hello",
        "complex": "The quick brown fox jumps over the lazy dog!",
        "unicode": "Hello 世界! 🌍",
        "numbers": "12345",
        "mixed": "Test123!@#",
        "palindrome": "racecar",
        "empty": "",
        "whitespace": "   ",
        "long": "a" * 1000,
        "max_length": "a" * 10000,
        "too_long": "a" * 10001
    }

@pytest.mark.parametrize("text,expected", [
    ("hello", "olleh"),
    ("12345", "54321"),
    ("a", "a"),
    ("", ""),
    ("Hello World!", "!dlroW olleH"),
])
@pytest.mark.asyncio
async def test_reverse_string_parametrized(text, expected):
    """Parametrized test for string reversal"""
    result = await reverse_string_activity(text)
    assert result.reversed_text == expected

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 