from typing import Dict, Any, List, Tuple, Optional
from uuid import uuid4
import os
from pathlib import Path

from app.models.schemas import Intent, IntentType, Message
from automation.handlers.response_generator import ResponseGenerator
from automation.tasks.file_operations import FileOperationTask
from automation.tasks.reminder_task import ReminderTask
from automation.tasks.script_runner import ScriptRunnerTask
from app.core.logging_config import get_logger


logger = get_logger(__name__)


class CommandHandler:
    def __init__(self):
        self.response_generator = ResponseGenerator()
        self.file_task = FileOperationTask()
        self.reminder_task = ReminderTask()
        self.script_task = ScriptRunnerTask()
    
    async def handle(
        self,
        intent: Intent,
        message: str,
        context: Dict[str, Any],
        history: List[Message],
    ) -> Tuple[str, Optional[str]]:
        logger.info(f"Handling intent: {intent.type} with confidence {intent.confidence}")
        
        active_mode = context.get("active_mode", "chat")
        
        mode_check = self._check_mode_compatibility(active_mode, intent.type)
        if not mode_check["allowed"]:
            return mode_check["message"], None
        
        if intent.type == IntentType.FILE_OPERATION:
            return await self._handle_file_operation(intent, message)
        
        elif intent.type == IntentType.SCHEDULE_REMINDER:
            return await self._handle_reminder(intent, message)
        
        elif intent.type == IntentType.RUN_SCRIPT:
            return await self._handle_script_execution(intent, message)
        
        elif intent.type == IntentType.SEARCH:
            return await self._handle_search(intent, message)
        
        elif intent.type == IntentType.SYSTEM_INFO:
            return await self._handle_system_info(intent, message)
        
        else:
            return await self._handle_chat(intent, message, history)
    
    def _check_mode_compatibility(self, active_mode: str, intent_type: IntentType) -> Dict[str, Any]:
        mode_messages = {
            "file_operation": "I can only do file operations right now. Please ask about creating, reading, deleting, or managing files.",
            "schedule_reminder": "I can only schedule reminders right now. Please ask about setting reminders or alarms.",
            "run_script": "I can only run scripts right now. Please ask about executing scripts or programs.",
            "search": "I can only search right now. Please ask about finding files or information.",
            "system_info": "I can only provide system information right now. Please ask about time, date, or system status.",
        }
        
        if active_mode == "chat":
            return {"allowed": True, "message": None}
        
        mode_to_intent = {
            "file_operation": IntentType.FILE_OPERATION,
            "schedule_reminder": IntentType.SCHEDULE_REMINDER,
            "run_script": IntentType.RUN_SCRIPT,
            "search": IntentType.SEARCH,
            "system_info": IntentType.SYSTEM_INFO,
        }
        
        expected_intent = mode_to_intent.get(active_mode)
        
        if expected_intent and intent_type != expected_intent:
            return {
                "allowed": False,
                "message": mode_messages.get(active_mode, "I can only handle specific tasks in this mode.")
            }
        
        return {"allowed": True, "message": None}
    
    async def _handle_file_operation(
        self, intent: Intent, message: str
    ) -> Tuple[str, Optional[str]]:
        entities = intent.entities
        operation = entities.get("operation", "create")
        file_path = entities.get("file_path", entities.get("directory_path"))
        
        message_lower = message.lower()
        
        if not operation:
            if "folder" in message_lower or "directory" in message_lower:
                operation = "create_folder"
            elif "create" in message_lower:
                operation = "create"
        
        if "folder" in message_lower or "directory" in message_lower:
            operation = "create_folder"
        
        if not file_path:
            file_path = self._extract_filename_from_message(message)
        
        if not file_path:
            return "I can help you with files. Please specify the file or folder name.", None
        
        try:
            result = await self._execute_file_operation(operation, file_path, message)
            return result["message"], None
        except Exception as e:
            logger.error(f"File operation failed: {e}")
            return f"Sorry, I couldn't {operation} the file: {str(e)}", None
    
    def _extract_filename_from_message(self, message: str) -> Optional[str]:
        import re
        
        quoted = re.findall(r'["\']([^"\']+)["\']', message)
        if quoted:
            return quoted[0]
        
        words = message.split()
        
        trigger_words = ["named", "called", "name", "titled", "as"]
        for i, word in enumerate(words):
            if word.lower() in trigger_words:
                if i + 1 < len(words):
                    return words[i + 1].strip('"\'')
        
        stop_words = {
            'create', 'make', 'new', 'a', 'an', 'the', 'in', 'on', 'at',
            'folder', 'file', 'directory', 'named', 'called', 'please',
            'can', 'you', 'me', 'i', 'want', 'need', 'would', 'like',
            'desktop', 'to', 'for', 'with', 'my', 'some', 'this', 'that'
        }
        
        potential_names = []
        for word in words:
            clean = word.strip('.,!?"\'"')
            if clean and len(clean) > 1 and clean.lower() not in stop_words:
                potential_names.append(clean)
        
        if potential_names:
            return potential_names[-1]
        
        return None
    
    async def _execute_file_operation(
        self, operation: str, file_path: str, original_message: str
    ) -> Dict[str, Any]:
        home = str(Path.home())
        desktop = os.path.join(home, "Desktop")
        
        if "desktop" in original_message.lower():
            full_path = os.path.join(desktop, file_path)
        else:
            full_path = file_path
        
        if operation in ["create_folder", "create"] and ("folder" in original_message.lower() or "directory" in original_message.lower()):
            os.makedirs(full_path, exist_ok=True)
            return {
                "success": True,
                "message": f"Created folder '{file_path}' successfully!",
                "path": full_path
            }
        
        elif operation == "create":
            parameters = {
                "operation": "create",
                "file_path": full_path,
                "content": ""
            }
            result = await self.file_task.execute(parameters)
            return {
                "success": result["success"],
                "message": f"Created file '{file_path}' successfully!",
                "path": full_path
            }
        
        elif operation == "read":
            parameters = {
                "operation": "read",
                "file_path": full_path
            }
            result = await self.file_task.execute(parameters)
            content_preview = result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"]
            return {
                "success": True,
                "message": f"File content:\n{content_preview}",
                "content": result["content"]
            }
        
        elif operation == "delete":
            parameters = {
                "operation": "delete",
                "file_path": full_path
            }
            result = await self.file_task.execute(parameters)
            return {
                "success": result["success"],
                "message": f"Deleted '{file_path}' successfully!",
            }
        
        else:
            return {
                "success": False,
                "message": f"I'll help you {operation} the file '{file_path}'."
            }
    
    async def _handle_reminder(
        self, intent: Intent, message: str
    ) -> Tuple[str, Optional[str]]:
        entities = intent.entities
        scheduled_time = entities.get("scheduled_datetime")
        
        reminder_message = message
        reminder_type = "reminder"
        
        if any(word in message.lower() for word in ["meeting", "event", "appointment", "schedule"]):
            reminder_type = "calendar"
        
        try:
            parameters = {
                "message": reminder_message,
                "scheduled_time": scheduled_time,
                "type": reminder_type
            }
            result = await self.reminder_task.execute(parameters)
            
            if result.get("success"):
                if result.get("app") == "macOS Reminders":
                    return f"Created reminder in your macOS Reminders app: {result.get('title')}", None
                elif result.get("app") == "macOS Calendar":
                    return f"Created event in your macOS Calendar: {result.get('title')}", None
                else:
                    return "Reminder created!", None
            else:
                return f"Error: {result.get('message', 'Failed to create reminder')}", None
                
        except Exception as e:
            return f"Couldn't set reminder: {str(e)}", None
    
    async def _handle_script_execution(
        self, intent: Intent, message: str
    ) -> Tuple[str, Optional[str]]:
        entities = intent.entities
        script_name = entities.get("script_name")
        
        if not script_name:
            return "Which script would you like me to run?", None
        
        try:
            parameters = {
                "script_path": script_name,
                "args": []
            }
            result = await self.script_task.execute(parameters)
            
            if result["success"]:
                output = result["stdout"][:300]
                return f"Script executed successfully!\n\nOutput:\n{output}", None
            else:
                return f"Script failed: {result.get('error', 'Unknown error')}", None
        except Exception as e:
            return f"Couldn't execute script: {str(e)}", None
    
    async def _handle_search(
        self, intent: Intent, message: str
    ) -> Tuple[str, Optional[str]]:
        entities = intent.entities
        search_query = message
        
        import os
        from pathlib import Path
        
        home = str(Path.home())
        desktop = os.path.join(home, "Desktop")
        
        search_locations = [desktop, home]
        
        results = []
        search_term = None
        
        words = message.lower().split()
        if 'named' in words:
            idx = words.index('named')
            if idx + 1 < len(words):
                search_term = words[idx + 1].strip('"\'')
        elif 'called' in words:
            idx = words.index('called')
            if idx + 1 < len(words):
                search_term = words[idx + 1].strip('"\'')
        else:
            import re
            quoted = re.findall(r'["\']([^"\']+)["\']', message)
            if quoted:
                search_term = quoted[0]
        
        if not search_term:
            potential = [w.strip('.,!?"\'') for w in words if len(w) > 3 and w not in ['find', 'search', 'folder', 'file', 'where', 'locate', 'help', 'please', 'exact', 'location', 'this', 'that', 'tell']]
            if potential:
                search_term = potential[-1]
        
        if search_term:
            for location in search_locations:
                try:
                    for root, dirs, files in os.walk(location):
                        if search_term.lower() in root.lower():
                            results.append(root)
                        
                        for d in dirs:
                            if search_term.lower() in d.lower():
                                full_path = os.path.join(root, d)
                                results.append(full_path)
                        
                        for f in files:
                            if search_term.lower() in f.lower():
                                full_path = os.path.join(root, f)
                                results.append(full_path)
                        
                        if len(results) >= 10:
                            break
                    
                    if len(results) >= 10:
                        break
                except PermissionError:
                    continue
        
        if results:
            response = f"Found {len(results)} result(s) for '{search_term}':\n\n"
            for i, path in enumerate(results[:5], 1):
                response += f"{i}. {path}\n"
            
            if len(results) > 5:
                response += f"\n... and {len(results) - 5} more results"
        else:
            response = f"No results found for '{search_term}'" if search_term else "Please specify what you want to search for."
        
        return response, None
    
    async def _handle_system_info(
        self, intent: Intent, message: str
    ) -> Tuple[str, Optional[str]]:
        response = await self.response_generator.generate_system_info_response()
        return response, None
    
    async def _handle_chat(
        self, intent: Intent, message: str, history: List[Message]
    ) -> Tuple[str, Optional[str]]:
        response = await self.response_generator.generate_chat_response(
            message, history
        )
        return response, None

