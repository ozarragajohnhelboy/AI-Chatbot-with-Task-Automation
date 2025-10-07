import subprocess
import platform
from typing import Dict, Any
from datetime import datetime

from app.core.logging_config import get_logger


logger = get_logger(__name__)


class MacOSReminders:
    def __init__(self):
        self.is_macos = platform.system() == "Darwin"
        self.reminders_available = self._check_reminders_app()
    
    def _check_reminders_app(self) -> bool:
        if not self.is_macos:
            return False
        
        try:
            applescript = '''
            tell application "System Events"
                return exists application process "Reminders"
            end tell
            '''
            subprocess.run(['osascript', '-e', applescript], 
                         capture_output=True, 
                         text=True, 
                         check=True)
            return True
        except Exception:
            return True
    
    def create_reminder(
        self, 
        title: str, 
        notes: str = "", 
        due_date: str = None,
        list_name: str = "Reminders"
    ) -> Dict[str, Any]:
        
        if not self.is_macos:
            return {
                "success": False,
                "message": "macOS Reminders is only available on Mac devices",
                "platform": platform.system()
            }
        
        try:
            if due_date:
                applescript = f'''
                tell application "Reminders"
                    tell list "{list_name}"
                        make new reminder with properties {{name:"{title}", body:"{notes}", due date:date "{due_date}"}}
                    end tell
                end tell
                '''
            else:
                applescript = f'''
                tell application "Reminders"
                    tell list "{list_name}"
                        make new reminder with properties {{name:"{title}", body:"{notes}"}}
                    end tell
                end tell
                '''
            
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Created reminder in macOS Reminders app: {title}")
            
            return {
                "success": True,
                "message": f"Reminder '{title}' created in your macOS Reminders app",
                "app": "macOS Reminders",
                "list": list_name,
                "title": title,
                "due_date": due_date
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create reminder: {e.stderr}")
            return {
                "success": False,
                "message": f"Failed to create reminder: {e.stderr}",
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Error creating reminder: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "error": str(e)
            }
    
    def create_calendar_event(
        self,
        title: str,
        start_date: str,
        notes: str = "",
        calendar_name: str = None
    ) -> Dict[str, Any]:
        
        if not self.is_macos:
            return {
                "success": False,
                "message": "macOS Calendar is only available on Mac devices"
            }
        
        try:
            if not calendar_name:
                calendar_name = self._get_default_calendar()
            
            formatted_date = self._format_date_for_applescript(start_date)
            
            applescript = f'''tell application "Calendar"
tell calendar "{calendar_name}"
    set startTime to {formatted_date}
    set endTime to startTime + (1 * hours)
    make new event with properties {{summary:"{title}", start date:startTime, end date:endTime, description:"{notes}"}}
end tell
end tell'''
            
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Created calendar event: {title}")
            
            return {
                "success": True,
                "message": f"Event '{title}' created in your macOS Calendar",
                "app": "macOS Calendar",
                "title": title,
                "start_date": start_date,
                "calendar": calendar_name
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"AppleScript error: {e.stderr}")
            return {
                "success": False,
                "message": f"Failed to create calendar event. Calendar '{calendar_name}' not found.",
                "error": e.stderr
            }
        except Exception as e:
            logger.error(f"Error creating calendar event: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "error": str(e)
            }
    
    def _get_default_calendar(self) -> str:
        try:
            applescript = '''
            tell application "Calendar"
                return name of first calendar
            end tell
            '''
            
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                calendar_name = result.stdout.strip()
                logger.info(f"Found default calendar: {calendar_name}")
                return calendar_name
            else:
                logger.warning("Could not get default calendar, using 'Home'")
                return "Home"
                
        except Exception as e:
            logger.warning(f"Error getting default calendar: {e}, using 'Home'")
            return "Home"
    
    def _format_date_for_applescript(self, date_str: str) -> str:
        try:
            from datetime import datetime
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(date_str, '%m/%d/%Y %H:%M:%S')
            
            return f'date "{dt.strftime("%m/%d/%Y %H:%M:%S")}"'
        except Exception:
            return f'date "{date_str}"'
    
    def get_available_apps(self) -> Dict[str, Any]:
        apps = {
            "platform": platform.system(),
            "is_mac": self.is_macos,
            "available_apps": []
        }
        
        if self.is_macos:
            apps["available_apps"] = [
                {
                    "name": "Reminders",
                    "type": "reminder",
                    "available": True
                },
                {
                    "name": "Calendar",
                    "type": "calendar",
                    "available": True
                }
            ]
        
        return apps

