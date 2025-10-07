from fastapi import APIRouter, HTTPException, BackgroundTasks
from uuid import uuid4

from app.models.schemas import TaskRequest, TaskResponse, TaskStatus
from automation.tasks.executor import TaskExecutor
from app.core.logging_config import get_logger


logger = get_logger(__name__)
router = APIRouter()


task_storage = {}


@router.post("/tasks", response_model=TaskResponse)
async def create_task(request: TaskRequest, background_tasks: BackgroundTasks):
    try:
        task_id = str(uuid4())
        
        task_response = TaskResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
        )
        
        task_storage[task_id] = task_response
        
        executor = TaskExecutor()
        background_tasks.add_task(
            executor.execute_task,
            task_id=task_id,
            task_type=request.task_type,
            parameters=request.parameters,
            storage=task_storage,
        )
        
        return task_response
        
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task_storage[task_id]

