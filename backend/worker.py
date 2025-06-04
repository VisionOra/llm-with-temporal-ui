import asyncio
import os
import logging
from temporalio.worker import Worker
from temporalio.client import Client

from temporal_workflows import (
    ReverseStringWorkflow,
    reverse_string_activity,
    validate_input_activity
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """
    Main function to start the Temporal worker.
    The worker processes workflows and activities.
    """
    # Get configuration from environment
    temporal_host = os.getenv("TEMPORAL_HOST", "localhost:7233")
    namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
    task_queue = os.getenv("TEMPORAL_TASK_QUEUE", "reverse-string-task-queue")
    
    logger.info(f"Connecting to Temporal at {temporal_host}")
    logger.info(f"Namespace: {namespace}")
    logger.info(f"Task queue: {task_queue}")
    
    try:
        # Connect to Temporal
        client = await Client.connect(
            temporal_host,
            namespace=namespace,
        )
        
        logger.info("Successfully connected to Temporal server")
        
        # Create and run worker
        worker = Worker(
            client,
            task_queue=task_queue,
            workflows=[ReverseStringWorkflow],
            activities=[reverse_string_activity, validate_input_activity],
        )
        
        logger.info(f"Starting worker on task queue: {task_queue}")
        logger.info("Worker is running. Press Ctrl+C to stop.")
        
        # Run the worker
        await worker.run()
        
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"Worker error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 