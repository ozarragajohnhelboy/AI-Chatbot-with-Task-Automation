import re
from typing import Dict, Any, List
from datetime import datetime, timedelta
import os

from app.core.logging_config import get_logger


logger = get_logger(__name__)


class EntityExtractorModel:
    def __init__(self):
        self.entity_patterns = {
            "file_path": r'["\']([^"\']+\.[a-zA-Z0-9]+)["\']|(?:file|path):\s*([^\s]+)',
            "directory_path": r'["\']([^"\']+/)["\']|(?:directory|folder):\s*([^\s]+)',
            "time": r'\b(\d{1,2}:\d{2}(?:\s*[AP]M)?)\b',
            "date": r'\b(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|\d{1,2}-\d{1,2}-\d{4})\b',
            "relative_time": r'\b(tomorrow|today|tonight|later|next week|next month)\b',
            "script_name": r'["\']([^"\']+\.py)["\']|\b(\w+\.py)\b',
            "command": r'(?:run|execute)\s+["\']([^"\']+)["\']',
            "number": r'\b(\d+)\b',
            "month_date": r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2}),?\s+(\d{4})\b',
        }
    
    async def extract(self, text: str) -> Dict[str, Any]:
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    values = [m for match in matches for m in match if m]
                else:
                    values = matches
                
                if values:
                    entities[entity_type] = values[0] if len(values) == 1 else values
        
        extracted_time = self._extract_time_from_message(text)
        if extracted_time:
            entities["extracted_time"] = extracted_time
        
        extracted_date = self._extract_date_from_message(text)
        if extracted_date:
            entities["extracted_date"] = extracted_date
        
        if "relative_time" in entities:
            entities["scheduled_datetime"] = self._parse_relative_time(
                entities["relative_time"]
            )
        elif "date" in entities and "time" in entities:
            entities["scheduled_datetime"] = f"{entities['date']} {entities['time']}"
        elif "date" in entities and extracted_time:
            entities["scheduled_datetime"] = f"{entities['date']} {extracted_time}"
        elif extracted_date and extracted_time:
            entities["scheduled_datetime"] = f"{extracted_date} {extracted_time}"
        elif "month_date" in entities:
            formatted_date = self._format_month_date(entities["month_date"])
            if extracted_time:
                entities["scheduled_datetime"] = f"{formatted_date} {extracted_time}"
            else:
                entities["scheduled_datetime"] = formatted_date
        
        self._extract_file_operations(text, entities)
        
        return entities
    
    def _parse_relative_time(self, relative_time: str) -> str:
        now = datetime.now()
        relative_time = relative_time.lower()
        
        if relative_time == "tomorrow":
            target = now + timedelta(days=1)
            return target.replace(hour=9, minute=0).isoformat()
        elif relative_time == "today":
            return now.replace(minute=0, second=0).isoformat()
        elif relative_time == "tonight":
            return now.replace(hour=20, minute=0, second=0).isoformat()
        elif relative_time == "later":
            target = now + timedelta(hours=2)
            return target.isoformat()
        elif relative_time == "next week":
            target = now + timedelta(days=7)
            return target.replace(hour=9, minute=0).isoformat()
        elif relative_time == "next month":
            target = now + timedelta(days=30)
            return target.replace(hour=9, minute=0).isoformat()
        
        return now.isoformat()
    
    def _extract_time_from_message(self, message: str) -> str:
        import re
        
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)',
            r'(\d{1,2})\s*(am|pm)',
            r'at\s+(\d{1,2}):(\d{2})',
            r'at\s+(\d{1,2})',
        ]
        
        message_lower = message.lower()
        
        for pattern in time_patterns:
            match = re.search(pattern, message_lower)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    hour = int(groups[0])
                    
                    if groups[1] in ['am', 'pm']:
                        minute = 0
                        ampm = groups[1]
                    else:
                        minute = int(groups[1]) if groups[1].isdigit() else 0
                        ampm = groups[2] if len(groups) > 2 and groups[2] in ['am', 'pm'] else None
                    
                    if ampm:
                        if ampm == 'pm' and hour != 12:
                            hour += 12
                        elif ampm == 'am' and hour == 12:
                            hour = 0
                    
                    return f"{hour:02d}:{minute:02d}:00"
        
        return None
    
    def _extract_date_from_message(self, message: str) -> str:
        import re
        from datetime import datetime
        
        month_names = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        
        message_lower = message.lower()
        
        pattern = r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2}),?\s+(\d{4})\b'
        match = re.search(pattern, message_lower)
        
        if match:
            month_name, day, year = match.groups()
            month_num = month_names[month_name]
            
            try:
                dt = datetime(int(year), month_num, int(day))
                return dt.strftime('%m/%d/%Y')
            except ValueError:
                return None
        
        return None
    
    def _format_month_date(self, month_date_tuple) -> str:
        from datetime import datetime
        
        month_names = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        
        if isinstance(month_date_tuple, tuple) and len(month_date_tuple) >= 3:
            month_name, day, year = month_date_tuple[:3]
            month_num = month_names.get(month_name.lower(), 1)
            
            try:
                dt = datetime(int(year), month_num, int(day))
                return dt.strftime('%m/%d/%Y')
            except ValueError:
                return None
        
        return None
    
    def _extract_file_operations(self, text: str, entities: Dict[str, Any]):
        operations_map = {
            'create': ['create', 'make', 'new', 'add', 'build', 'generate'],
            'open': ['open', 'show', 'display', 'view'],
            'read': ['read', 'see', 'check', 'look at'],
            'delete': ['delete', 'remove', 'erase', 'trash', 'clear'],
            'move': ['move', 'transfer', 'relocate', 'shift'],
            'copy': ['copy', 'duplicate', 'clone'],
            'write': ['write', 'save', 'store', 'put'],
            'rename': ['rename', 'change name'],
        }
        
        text_lower = text.lower()
        
        for base_op, variations in operations_map.items():
            for variation in variations:
                if variation in text_lower:
                    entities["operation"] = base_op
                    return
        
        if 'folder' in text_lower or 'directory' in text_lower:
            if 'create' not in entities and any(word in text_lower for word in ['make', 'new', 'create', 'build']):
                entities["operation"] = 'create'

