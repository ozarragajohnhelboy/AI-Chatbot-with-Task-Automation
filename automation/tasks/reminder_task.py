from typing import Dict, Any
from datetime import datetime

from automation.tasks.device_detector import DeviceDetector
from automation.tasks.macos_reminders import MacOSReminders
from automation.tasks.windows_calendar import WindowsCalendar
from app.core.logging_config import get_logger


logger = get_logger(__name__)


class ReminderTask:
    def __init__(self):
        self.device_detector = DeviceDetector()
        self.device_info = self.device_detector.get_device_info()
        
        logger.info(f"Device detected: {self.device_info['os']} ({self.device_info['machine']})")
        logger.info(f"Available apps: {[app['name'] for app in self.device_info['available_apps']]}")
        
        self.macos_reminders = None
        self.windows_calendar = None
        
        if self.device_info['os'] == "Darwin":
            self.macos_reminders = MacOSReminders()
        elif self.device_info['os'] == "Windows":
            self.windows_calendar = WindowsCalendar()
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        message = parameters.get("message", "Reminder")
        scheduled_time = parameters.get("scheduled_time")
        reminder_type = parameters.get("type", "reminder")
        
        preferred_app = None
        if reminder_type == "calendar":
            preferred_app = self.device_info.get('preferred_calendar_app')
        else:
            preferred_app = self.device_info.get('preferred_reminder_app')
        
        if not preferred_app:
            preferred_app = self.device_info.get('preferred_calendar_app')
        
        if not preferred_app:
            return await self._fallback_reminder(message, scheduled_time)
        
        if preferred_app['platform'] == "macOS" and self.macos_reminders:
            return await self._create_macos_reminder(message, scheduled_time, reminder_type)
        elif preferred_app['platform'] == "Windows" and self.windows_calendar:
            return await self._create_windows_reminder(message, scheduled_time)
        else:
            return await self._fallback_reminder(message, scheduled_time)
    
    async def _create_macos_reminder(
        self, 
        message: str, 
        scheduled_time: str = None,
        reminder_type: str = "reminder"
    ) -> Dict[str, Any]:
        
        title = self._extract_title_from_message(message)
        notes = message
        
        if reminder_type == "calendar" or "meeting" in message.lower() or "event" in message.lower():
            if scheduled_time:
                result = self.macos_reminders.create_calendar_event(
                    title=title,
                    start_date=scheduled_time,
                    notes=notes
                )
            else:
                result = self.macos_reminders.create_calendar_event(
                    title=title,
                    start_date=datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
                    notes=notes
                )
        else:
            result = self.macos_reminders.create_reminder(
                title=title,
                notes=notes,
                due_date=scheduled_time if scheduled_time else None
            )
        
        return result
    
    def _extract_title_from_message(self, message: str) -> str:
        words = message.split()
        
        stop_words = ['remind', 'me', 'to', 'about', 'for', 'at', 'tomorrow', 'today', 'later']
        
        title_words = [w for w in words if w.lower() not in stop_words]
        
        if title_words:
            return ' '.join(title_words[:5])
        
        return message[:50]
    
    async def _create_windows_reminder(
        self,
        message: str,
        scheduled_time: str = None
    ) -> Dict[str, Any]:
        title = self._extract_title_from_message(message)
        
        result = self.windows_calendar.create_event(
            title=title,
            start_date=scheduled_time,
            notes=message
        )
        
        return result
    
    async def _fallback_reminder(self, message: str, scheduled_time: str = None) -> Dict[str, Any]:
        logger.info(f"Reminder created: {message}")
        
        os_name = self.device_info['os']
        available_apps = self.device_info['available_apps']
        
        if not available_apps:
            note = f"No calendar/reminder apps found on {os_name}. Reminder logged locally."
        else:
            note = f"Reminder logged (integration not yet implemented for {os_name})"
        
        return {
            "operation": "reminder",
            "message": message,
            "scheduled_time": scheduled_time,
            "success": True,
            "note": note,
            "device": os_name
        }

