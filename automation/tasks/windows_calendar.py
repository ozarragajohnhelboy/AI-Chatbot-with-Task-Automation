import subprocess
from typing import Dict, Any
from datetime import datetime

from app.core.logging_config import get_logger


logger = get_logger(__name__)


class WindowsCalendar:
    def create_event(
        self,
        title: str,
        start_date: str = None,
        notes: str = ""
    ) -> Dict[str, Any]:
        try:
            powershell_script = f'''
            $outlook = New-Object -ComObject Outlook.Application
            $appointment = $outlook.CreateItem(1)
            $appointment.Subject = "{title}"
            $appointment.Body = "{notes}"
            $appointment.Save()
            '''
            
            result = subprocess.run(
                ['powershell', '-Command', powershell_script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                logger.info(f"Created Windows calendar event: {title}")
                return {
                    "success": True,
                    "message": f"Event '{title}' created in Windows Calendar",
                    "app": "Windows Calendar"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to create event: {result.stderr}"
                }
        except Exception as e:
            logger.error(f"Error creating Windows calendar event: {e}")
            return {
                "success": False,
                "message": str(e)
            }

