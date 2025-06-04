import os
import uuid
import asyncio
from typing import Dict, Any, Optional
from temporalio.client import Client, WorkflowFailureError
from temporalio.common import WorkflowIDReusePolicy
import logging

from temporal_workflows import ReverseStringWorkflow

logger = logging.getLogger(__name__)

class TemporalClient:
    """
    Temporal client service for executing workflows.
    Handles connection management and workflow execution.
    """
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
        self.target_host = os.getenv("TEMPORAL_HOST", "localhost:7233")
        self.task_queue = os.getenv("TEMPORAL_TASK_QUEUE", "reverse-string-task-queue")
    
    async def _ensure_connected(self) -> Client:
        """Ensure we have a connected Temporal client"""
        if self.client is None:
            try:
                self.client = await Client.connect(
                    self.target_host,
                    namespace=self.namespace,
                )
                logger.info(f"Connected to Temporal at {self.target_host}, namespace: {self.namespace}")
            except Exception as e:
                logger.error(f"Failed to connect to Temporal: {e}")
                raise ConnectionError(f"Cannot connect to Temporal server: {e}")
        
        return self.client
    
    async def execute_reverse_workflow(self, text: str) -> Dict[str, Any]:
        """
        Execute the reverse string workflow.
        
        Args:
            text: The string to reverse
            
        Returns:
            Dict containing workflow result and metadata
        """
        try:
            client = await self._ensure_connected()
            
            # Generate unique workflow ID
            workflow_id = f"reverse-string-{uuid.uuid4().hex[:8]}"
            
            logger.info(f"Starting workflow {workflow_id} for text: '{text[:50]}...'")
            
            # Start the workflow
            handle = await client.start_workflow(
                ReverseStringWorkflow.run,
                text,
                id=workflow_id,
                task_queue=self.task_queue,
                id_reuse_policy=WorkflowIDReusePolicy.ALLOW_DUPLICATE,
            )
            
            # Wait for workflow completion
            result = await handle.result()
            
            logger.info(f"Workflow {workflow_id} completed successfully")
            
            return {
                "workflow_id": workflow_id,
                "reversed_text": result.get("reversed_text", ""),
                "original_text": result.get("original_text", text),
                "processing_time_ms": result.get("processing_time_ms", 0),
                "success": result.get("success", True),
                "error": result.get("error")
            }
            
        except WorkflowFailureError as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                "workflow_id": workflow_id if 'workflow_id' in locals() else "unknown",
                "reversed_text": "",
                "original_text": text,
                "processing_time_ms": 0,
                "success": False,
                "error": f"Workflow failed: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            return {
                "workflow_id": workflow_id if 'workflow_id' in locals() else "unknown",
                "reversed_text": "",
                "original_text": text,
                "processing_time_ms": 0,
                "success": False,
                "error": str(e)
            }
    
    async def health_check(self) -> bool:
        """
        Check if Temporal connection is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            client = await self._ensure_connected()
            
            # Try to describe the namespace as a health check
            await client.describe_namespace()
            return True
            
        except Exception as e:
            logger.warning(f"Temporal health check failed: {e}")
            return False
    
    async def close(self):
        """Close the Temporal client connection"""
        if self.client:
            await self.client.close()
            self.client = None
            logger.info("Temporal client connection closed") 