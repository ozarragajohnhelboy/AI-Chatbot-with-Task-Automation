from typing import Dict, Any, List
from pathlib import Path
import json
from datetime import datetime

from app.core.logging_config import get_logger


logger = get_logger(__name__)


class FeedbackProcessor:
    def __init__(self):
        self.feedback_dir = Path("data/feedback")
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        self.feedback_file = self.feedback_dir / "feedback_log.jsonl"
    
    async def process_feedback(self, feedback: Dict[str, Any]):
        feedback["timestamp"] = datetime.utcnow().isoformat()
        
        with open(self.feedback_file, "a") as f:
            f.write(json.dumps(feedback) + "\n")
        
        logger.info(f"Processed feedback for session {feedback.get('session_id')}")
        
        await self._update_training_data(feedback)
    
    async def _update_training_data(self, feedback: Dict[str, Any]):
        training_data_file = self.feedback_dir / "training_corrections.jsonl"
        
        if feedback.get("expected_intent"):
            training_sample = {
                "text": feedback["message"],
                "intent": feedback["expected_intent"],
                "timestamp": feedback["timestamp"],
            }
            
            with open(training_data_file, "a") as f:
                f.write(json.dumps(training_sample) + "\n")
            
            logger.info("Added training correction")
    
    async def get_feedback_stats(self) -> Dict[str, Any]:
        if not self.feedback_file.exists():
            return {"total_feedback": 0, "by_rating": {}}
        
        feedback_items = []
        with open(self.feedback_file, "r") as f:
            for line in f:
                feedback_items.append(json.loads(line))
        
        rating_counts = {}
        for item in feedback_items:
            rating = item.get("rating")
            if rating:
                rating_counts[rating] = rating_counts.get(rating, 0) + 1
        
        return {
            "total_feedback": len(feedback_items),
            "by_rating": rating_counts,
        }

