import platform
import subprocess
import os
from typing import Dict, List, Any

from app.core.logging_config import get_logger


logger = get_logger(__name__)


class DeviceDetector:
    def __init__(self):
        self.os_type = platform.system()
        self.os_version = platform.version()
        self.machine = platform.machine()
        self.available_apps = self._detect_available_apps()
    
    def _detect_available_apps(self) -> List[Dict[str, Any]]:
        apps = []
        
        if self.os_type == "Darwin":
            apps.extend(self._detect_macos_apps())
        elif self.os_type == "Windows":
            apps.extend(self._detect_windows_apps())
        elif self.os_type == "Linux":
            apps.extend(self._detect_linux_apps())
        
        return apps
    
    def _detect_macos_apps(self) -> List[Dict[str, Any]]:
        apps = []
        
        if self._check_app_exists_macos("Reminders"):
            apps.append({
                "name": "Reminders",
                "type": "reminder",
                "platform": "macOS",
                "available": True,
                "priority": 1
            })
        
        if self._check_app_exists_macos("Calendar"):
            apps.append({
                "name": "Calendar",
                "type": "calendar",
                "platform": "macOS",
                "available": True,
                "priority": 1
            })
        
        logger.info(f"macOS apps detected: {[app['name'] for app in apps]}")
        return apps
    
    def _check_app_exists_macos(self, app_name: str) -> bool:
        try:
            result = subprocess.run(
                ['osascript', '-e', f'exists application "{app_name}"'],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0
        except Exception:
            return True
    
    def _detect_windows_apps(self) -> List[Dict[str, Any]]:
        apps = []
        
        if self._check_windows_calendar():
            apps.append({
                "name": "Windows Calendar",
                "type": "calendar",
                "platform": "Windows",
                "available": True,
                "priority": 1
            })
        
        if self._check_outlook():
            apps.append({
                "name": "Outlook",
                "type": "calendar",
                "platform": "Windows",
                "available": True,
                "priority": 2
            })
        
        logger.info(f"Windows apps detected: {[app['name'] for app in apps]}")
        return apps
    
    def _check_windows_calendar(self) -> bool:
        try:
            result = subprocess.run(
                ['powershell', '-Command', 'Get-AppxPackage', '*WindowsCalendar*'],
                capture_output=True,
                timeout=3
            )
            return result.returncode == 0 and len(result.stdout) > 0
        except Exception:
            return False
    
    def _check_outlook(self) -> bool:
        outlook_paths = [
            r"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\OUTLOOK.EXE",
        ]
        return any(os.path.exists(path) for path in outlook_paths)
    
    def _detect_linux_apps(self) -> List[Dict[str, Any]]:
        apps = []
        
        if self._check_command_exists("gnome-calendar"):
            apps.append({
                "name": "GNOME Calendar",
                "type": "calendar",
                "platform": "Linux",
                "available": True,
                "priority": 1
            })
        
        if self._check_command_exists("evolution"):
            apps.append({
                "name": "Evolution",
                "type": "calendar",
                "platform": "Linux",
                "available": True,
                "priority": 2
            })
        
        logger.info(f"Linux apps detected: {[app['name'] for app in apps]}")
        return apps
    
    def _check_command_exists(self, command: str) -> bool:
        try:
            result = subprocess.run(
                ['which', command],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def get_preferred_reminder_app(self) -> Dict[str, Any]:
        reminder_apps = [app for app in self.available_apps if app['type'] == 'reminder']
        
        if reminder_apps:
            return sorted(reminder_apps, key=lambda x: x['priority'])[0]
        
        calendar_apps = [app for app in self.available_apps if app['type'] == 'calendar']
        if calendar_apps:
            return sorted(calendar_apps, key=lambda x: x['priority'])[0]
        
        return None
    
    def get_preferred_calendar_app(self) -> Dict[str, Any]:
        calendar_apps = [app for app in self.available_apps if app['type'] == 'calendar']
        
        if calendar_apps:
            return sorted(calendar_apps, key=lambda x: x['priority'])[0]
        
        return None
    
    def get_device_info(self) -> Dict[str, Any]:
        return {
            "os": self.os_type,
            "version": self.os_version,
            "machine": self.machine,
            "available_apps": self.available_apps,
            "preferred_reminder_app": self.get_preferred_reminder_app(),
            "preferred_calendar_app": self.get_preferred_calendar_app()
        }

