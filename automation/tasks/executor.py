import asyncio
from datetime import datetime
from typing import Dict, Any

from app.models.schemas import TaskStatus
from automation.tasks.file_operations import FileOperationTask
from automation.tasks.reminder_task import ReminderTask
from automation.tasks.script_runner import ScriptRunnerTask
from app.core.logging_config import get_logger


logger = get_logger(__name__)


class TaskExecutor:
    def __init__(self):
        self.task_handlers = {
            "file_operation": FileOperationTask(),
            "reminder": ReminderTask(),
            "script_runner": ScriptRunnerTask(),
        }
    
    async def execute_task(
        self,
        task_id: str,
        task_type: str,
        parameters: Dict[str, Any],
        storage: Dict,
    ):
        try:
            logger.info(f"Executing task {task_id} of type {task_type}")
            
            storage[task_id].status = TaskStatus.RUNNING
            
            handler = self.task_handlers.get(task_type)
            if not handler:
                raise ValueError(f"Unknown task type: {task_type}")
            
            result = await handler.execute(parameters)
            
            storage[task_id].status = TaskStatus.COMPLETED
            storage[task_id].result = result
            storage[task_id].completed_at = datetime.utcnow()
            
            logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {str(e)}", exc_info=True)
            storage[task_id].status = TaskStatus.FAILED
            storage[task_id].error = str(e)
            storage[task_id].completed_at = datetime.utcnow()

