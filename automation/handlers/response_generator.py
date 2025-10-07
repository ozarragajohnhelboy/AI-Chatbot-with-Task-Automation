from typing import List
import random
from datetime import datetime
import platform
import psutil
import subprocess
import os

from app.models.schemas import Message
from app.core.logging_config import get_logger


logger = get_logger(__name__)


class ResponseGenerator:
    def __init__(self):
        self.greeting_responses = [
            "Hello! How can I assist you today?",
            "Hi there! What can I help you with?",
            "Greetings! I'm here to help.",
            "Hey! What would you like me to do?",
        ]
        
        self.thanks_responses = [
            "You're welcome!",
            "Happy to help!",
            "My pleasure!",
            "Anytime!",
        ]
        
        self.goodbye_responses = [
            "Goodbye! Have a great day!",
            "See you later!",
            "Take care!",
            "Until next time!",
        ]
    
    async def generate_chat_response(
        self, message: str, history: List[Message]
    ) -> str:
        message_lower = message.lower()
        
        if any(greet in message_lower for greet in ["hello", "hi", "hey", "greetings"]):
            return random.choice(self.greeting_responses)
        
        if any(thanks in message_lower for thanks in ["thank", "thanks"]):
            return random.choice(self.thanks_responses)
        
        if any(bye in message_lower for bye in ["bye", "goodbye", "see you"]):
            return random.choice(self.goodbye_responses)
        
        if "what can you do" in message_lower or "help" in message_lower:
            return self._generate_help_response()
        
        if "joke" in message_lower:
            return self._generate_joke()
        
        return "I'm here to help! I can manage files, schedule reminders, run scripts, search for information, and chat with you."
    
    async def generate_search_response(self, query: str) -> str:
        return f"I'm searching for: {query}. Here's what I found..."
    
    async def generate_system_info_response(self) -> str:
        try:
            info = self._get_detailed_system_info()
            return info
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return "Unable to retrieve system information at the moment."
    
    def _get_detailed_system_info(self) -> str:
        info_lines = []
        
        current_time = datetime.now()
        info_lines.append(f"Current Time: {current_time.strftime('%I:%M:%S %p')}")
        info_lines.append(f"Current Date: {current_time.strftime('%A, %B %d, %Y')}")
        info_lines.append("")
        
        system_info = platform.uname()
        info_lines.append(f"Operating System: {system_info.system} {system_info.release}")
        info_lines.append(f"Architecture: {system_info.machine}")
        info_lines.append(f"Processor: {system_info.processor}")
        info_lines.append("")
        
        try:
            cpu_count = psutil.cpu_count()
            cpu_percent = psutil.cpu_percent(interval=1)
            info_lines.append(f"CPU Cores: {cpu_count}")
            info_lines.append(f"CPU Usage: {cpu_percent}%")
        except Exception:
            info_lines.append("CPU Info: Unable to retrieve")
        
        try:
            memory = psutil.virtual_memory()
            total_gb = memory.total / (1024**3)
            used_gb = memory.used / (1024**3)
            available_gb = memory.available / (1024**3)
            info_lines.append(f"Total RAM: {total_gb:.1f} GB")
            info_lines.append(f"Used RAM: {used_gb:.1f} GB")
            info_lines.append(f"Available RAM: {available_gb:.1f} GB")
            info_lines.append(f"Memory Usage: {memory.percent}%")
        except Exception:
            info_lines.append("Memory Info: Unable to retrieve")
        
        try:
            disk = psutil.disk_usage('/')
            total_disk = disk.total / (1024**3)
            used_disk = disk.used / (1024**3)
            free_disk = disk.free / (1024**3)
            info_lines.append(f"Total Disk Space: {total_disk:.1f} GB")
            info_lines.append(f"Used Disk Space: {used_disk:.1f} GB")
            info_lines.append(f"Free Disk Space: {free_disk:.1f} GB")
        except Exception:
            info_lines.append("Disk Info: Unable to retrieve")
        
        info_lines.append("")
        
        if system_info.system == "Darwin":
            mac_info = self._get_macos_specific_info()
            info_lines.extend(mac_info)
        elif system_info.system == "Windows":
            windows_info = self._get_windows_specific_info()
            info_lines.extend(windows_info)
        elif system_info.system == "Linux":
            linux_info = self._get_linux_specific_info()
            info_lines.extend(linux_info)
        
        return "\n".join(info_lines)
    
    def _get_macos_specific_info(self) -> List[str]:
        info = []
        try:
            result = subprocess.run(
                ['sw_vers'],
                capture_output=True,
                text=True,
                timeout=3
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'ProductName:' in line:
                        info.append(f"macOS Version: {line.split(':', 1)[1].strip()}")
                    elif 'ProductVersion:' in line:
                        info.append(f"macOS Build: {line.split(':', 1)[1].strip()}")
                    elif 'BuildVersion:' in line:
                        info.append(f"Build: {line.split(':', 1)[1].strip()}")
        except Exception:
            pass
        
        try:
            result = subprocess.run(
                ['system_profiler', 'SPHardwareDataType'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Model Name:' in line:
                        info.append(f"Mac Model: {line.split(':', 1)[1].strip()}")
                    elif 'Chip:' in line:
                        info.append(f"Processor Chip: {line.split(':', 1)[1].strip()}")
                    elif 'Serial Number:' in line:
                        info.append(f"Serial: {line.split(':', 1)[1].strip()}")
        except Exception:
            pass
        
        return info
    
    def _get_windows_specific_info(self) -> List[str]:
        info = []
        try:
            result = subprocess.run(
                ['powershell', '-Command', 'Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, TotalPhysicalMemory'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'WindowsProductName' in line:
                        info.append(f"Windows Edition: {line.split(':', 1)[1].strip()}")
                    elif 'WindowsVersion' in line:
                        info.append(f"Windows Version: {line.split(':', 1)[1].strip()}")
        except Exception:
            pass
        
        return info
    
    def _get_linux_specific_info(self) -> List[str]:
        info = []
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read()
                for line in content.split('\n'):
                    if line.startswith('PRETTY_NAME='):
                        distro = line.split('=', 1)[1].strip('"')
                        info.append(f"Linux Distribution: {distro}")
                    elif line.startswith('VERSION='):
                        version = line.split('=', 1)[1].strip('"')
                        info.append(f"Version: {version}")
        except Exception:
            pass
        
        try:
            result = subprocess.run(
                ['uname', '-r'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                kernel = result.stdout.strip()
                info.append(f"Kernel: {kernel}")
        except Exception:
            pass
        
        return info
    
    def _generate_help_response(self) -> str:
        return (
            "I can help you with:\n"
            "• File operations (create, open, delete, move, copy)\n"
            "• Schedule reminders and notifications\n"
            "• Run scripts and programs\n"
            "• Search for files and information\n"
            "• System information\n"
            "• General conversation\n\n"
            "Just tell me what you need!"
        )
    
    def _generate_joke(self) -> str:
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Why did the developer go broke? Because he used up all his cache!",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
        ]
        return random.choice(jokes)