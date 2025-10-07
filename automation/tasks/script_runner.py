import subprocess
from typing import Dict, Any
from pathlib import Path

from app.core.logging_config import get_logger


logger = get_logger(__name__)


class ScriptRunnerTask:
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        script_path = parameters.get("script_path")
        args = parameters.get("args", [])
        timeout = parameters.get("timeout", 300)
        
        if not script_path:
            raise ValueError("script_path is required")
        
        script_path = Path(script_path)
        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")
        
        command = self._build_command(script_path, args)
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True,
            )
            
            logger.info(f"Script executed successfully: {script_path}")
            return {
                "operation": "run_script",
                "script_path": str(script_path),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "success": True,
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"Script timeout: {script_path}")
            raise TimeoutError(f"Script execution timeout after {timeout}s")
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Script failed: {script_path}")
            return {
                "operation": "run_script",
                "script_path": str(script_path),
                "stdout": e.stdout,
                "stderr": e.stderr,
                "return_code": e.returncode,
                "success": False,
                "error": str(e),
            }
    
    def _build_command(self, script_path: Path, args: list) -> list:
        if script_path.suffix == ".py":
            return ["python", str(script_path)] + args
        elif script_path.suffix == ".sh":
            return ["bash", str(script_path)] + args
        else:
            return [str(script_path)] + args

