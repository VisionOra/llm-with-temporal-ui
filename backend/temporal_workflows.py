import asyncio
from datetime import timedelta
from temporalio import activity, workflow
from temporalio.common import RetryPolicy
from dataclasses import dataclass
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

@dataclass
class ReverseResult:
    """Result of string reversal workflow"""
    original_text: str
    reversed_text: str
    processing_time_ms: int

@activity.defn
async def reverse_string_activity(text: str) -> ReverseResult:
    """
    Activity to reverse a string.
    This demonstrates a simple Temporal activity.
    """
    import time
    start_time = time.time()
    
    try:
        # Simulate some processing time
        await asyncio.sleep(0.1)
        
        reversed_text = text[::-1]
        processing_time = int((time.time() - start_time) * 1000)
        
        logger.info(f"Reversed '{text}' to '{reversed_text}' in {processing_time}ms")
        
        return ReverseResult(
            original_text=text,
            reversed_text=reversed_text,
            processing_time_ms=processing_time
        )
    except Exception as e:
        logger.error(f"Error in reverse_string_activity: {e}")
        raise

@activity.defn
async def validate_input_activity(text: str) -> bool:
    """
    Activity to validate input text.
    Demonstrates activity chaining in workflows.
    """
    try:
        # Basic validation
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")
        
        if len(text) > 10000:
            raise ValueError("Input text too long (max 10,000 characters)")
        
        logger.info(f"Input validation passed for text of length {len(text)}")
        return True
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise

@workflow.defn
class ReverseStringWorkflow:
    """
    Temporal workflow to reverse a string.
    Demonstrates workflow definition with activities and error handling.
    """
    
    @workflow.run
    async def run(self, text: str) -> Dict[str, Any]:
        """
        Main workflow execution method.
        
        Args:
            text: The string to reverse
            
        Returns:
            Dict containing the workflow result
        """
        workflow_id = workflow.info().workflow_id
        
        try:
            # Step 1: Validate input
            await workflow.execute_activity(
                validate_input_activity,
                text,
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=10),
                    maximum_attempts=3,
                )
            )
            
            # Step 2: Reverse the string
            result = await workflow.execute_activity(
                reverse_string_activity,
                text,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=10),
                    maximum_attempts=3,
                )
            )
            
            return {
                "workflow_id": workflow_id,
                "success": True,
                "original_text": result.original_text,
                "reversed_text": result.reversed_text,
                "processing_time_ms": result.processing_time_ms,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed: {e}")
            return {
                "workflow_id": workflow_id,
                "success": False,
                "original_text": text,
                "reversed_text": "",
                "processing_time_ms": 0,
                "error": str(e)
            }

# Export workflow and activities for the worker
__all__ = ["ReverseStringWorkflow", "reverse_string_activity", "validate_input_activity"] 