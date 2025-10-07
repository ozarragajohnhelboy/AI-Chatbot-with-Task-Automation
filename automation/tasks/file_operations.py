import os
import shutil
from pathlib import Path
from typing import Dict, Any

from app.core.logging_config import get_logger


logger = get_logger(__name__)


class FileOperationTask:
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        operation = parameters.get("operation", "").lower()
        file_path = parameters.get("file_path")
        
        if operation == "create":
            return await self._create_file(file_path, parameters.get("content", ""))
        elif operation == "read":
            return await self._read_file(file_path)
        elif operation == "delete":
            return await self._delete_file(file_path)
        elif operation == "move":
            destination = parameters.get("destination")
            return await self._move_file(file_path, destination)
        elif operation == "copy":
            destination = parameters.get("destination")
            return await self._copy_file(file_path, destination)
        else:
            raise ValueError(f"Unsupported file operation: {operation}")
    
    async def _create_file(self, file_path: str, content: str) -> Dict[str, Any]:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            f.write(content)
        
        logger.info(f"Created file: {file_path}")
        return {"operation": "create", "file_path": str(path), "success": True}
    
    async def _read_file(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r') as f:
            content = f.read()
        
        logger.info(f"Read file: {file_path}")
        return {"operation": "read", "file_path": file_path, "content": content}
    
    async def _delete_file(self, file_path: str) -> Dict[str, Any]:
        path = Path(file_path)
        
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
        
        logger.info(f"Deleted: {file_path}")
        return {"operation": "delete", "file_path": file_path, "success": True}
    
    async def _move_file(self, source: str, destination: str) -> Dict[str, Any]:
        shutil.move(source, destination)
        
        logger.info(f"Moved file from {source} to {destination}")
        return {
            "operation": "move",
            "source": source,
            "destination": destination,
            "success": True,
        }
    
    async def _copy_file(self, source: str, destination: str) -> Dict[str, Any]:
        if Path(source).is_file():
            shutil.copy2(source, destination)
        else:
            shutil.copytree(source, destination)
        
        logger.info(f"Copied from {source} to {destination}")
        return {
            "operation": "copy",
            "source": source,
            "destination": destination,
            "success": True,
        }

