import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from typing import Tuple, Dict, List
import random


class IntentDataGenerator:
    def __init__(self, max_length: int = 50):
        self.max_length = max_length
        self.tokenizer = Tokenizer(oov_token="<OOV>")
        
        self.training_samples = {
            "chat": [
                "hello", "hi", "how are you", "what's up", "good morning",
                "good evening", "hey there", "greetings", "nice to meet you",
                "tell me a joke", "what can you do", "help me", "thanks",
                "thank you", "goodbye", "bye", "see you later", "talk to you later",
            ],
            "file_operation": [
                "open file document.txt", "create new file", "delete old files",
                "move file to folder", "copy this file", "read the file",
                "save this to file", "create folder named project",
                "open the document", "remove this file", "rename file to new name",
            ],
            "schedule_reminder": [
                "remind me tomorrow", "set alarm for 9am", "schedule meeting",
                "notify me later", "reminder at 5pm", "set reminder for next week",
                "schedule task for tomorrow", "remind me to call john",
                "set alarm tomorrow morning", "notify me in 2 hours",
            ],
            "run_script": [
                "run script.py", "execute the program", "start the application",
                "launch python script", "run command ls", "execute this code",
                "start the server", "run my script", "execute backup.py",
            ],
            "search": [
                "search for documents", "find my files", "look for recent emails",
                "where is my report", "find python files", "search in folder",
                "query database", "look up information", "find notes about project",
            ],
            "system_info": [
                "what time is it", "check system status", "show cpu usage",
                "memory usage", "disk space", "what's the date", "system info",
                "check processes", "show running tasks", "current weather",
            ],
            "unknown": [
                "asdfghjkl", "random text here", "blah blah blah",
                "xyz abc def", "nonsense input", "qwerty uiop",
            ],
        }
    
    def generate(self) -> Tuple[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray], int, Dict]:
        all_texts = []
        all_labels = []
        
        intent_map = {}
        for idx, (intent, samples) in enumerate(self.training_samples.items()):
            intent_map[intent] = idx
            
            augmented = samples.copy()
            for sample in samples[:5]:
                augmented.append(sample + " please")
                augmented.append(sample + " now")
            
            all_texts.extend(augmented)
            all_labels.extend([idx] * len(augmented))
        
        combined = list(zip(all_texts, all_labels))
        random.shuffle(combined)
        all_texts, all_labels = zip(*combined)
        
        self.tokenizer.fit_on_texts(all_texts)
        vocab_size = len(self.tokenizer.word_index) + 1
        
        sequences = self.tokenizer.texts_to_sequences(all_texts)
        padded = pad_sequences(
            sequences,
            maxlen=self.max_length,
            padding='post',
            truncating='post',
        )
        
        labels = np.array(all_labels)
        
        split_idx = int(0.8 * len(padded))
        
        X_train = padded[:split_idx]
        y_train = labels[:split_idx]
        X_val = padded[split_idx:]
        y_val = labels[split_idx:]
        
        return (X_train, y_train), (X_val, y_val), vocab_size, intent_map

