import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
from pathlib import Path

from app.core.logging_config import get_logger


logger = get_logger(__name__)


class VectorStore:
    def __init__(self):
        self.client = None
        self.collection = None
        self.embedding_model = None
    
    async def initialize(self):
        try:
            persist_dir = Path("data/chromadb")
            persist_dir.mkdir(parents=True, exist_ok=True)
            
            self.client = chromadb.Client(
                Settings(
                    persist_directory=str(persist_dir),
                    anonymized_telemetry=False,
                )
            )
            
            self.collection = self.client.get_or_create_collection(
                name="conversation_history",
                metadata={"description": "Chat interactions for learning"},
            )
            
            self.embedding_model = SentenceTransformer(
                'sentence-transformers/all-MiniLM-L6-v2'
            )
            
            logger.info("Vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
    
    async def add_interaction(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        intent: str,
    ):
        try:
            interaction_text = f"User: {user_message}\nAssistant: {assistant_response}"
            embedding = self.embedding_model.encode(interaction_text).tolist()
            
            interaction_id = f"{session_id}_{hash(interaction_text)}"
            
            self.collection.add(
                embeddings=[embedding],
                documents=[interaction_text],
                metadatas=[{
                    "session_id": session_id,
                    "user_message": user_message,
                    "assistant_response": assistant_response,
                    "intent": intent,
                }],
                ids=[interaction_id],
            )
            
            logger.debug(f"Added interaction to vector store: {interaction_id}")
            
        except Exception as e:
            logger.error(f"Error adding interaction to vector store: {e}")
    
    async def search_similar(
        self, query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        try:
            query_embedding = self.embedding_model.encode(query).tolist()
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
            )
            
            similar_interactions = []
            if results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    similar_interactions.append({
                        "document": doc,
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i] if "distances" in results else None,
                    })
            
            return similar_interactions
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    async def close(self):
        logger.info("Vector store closed")

