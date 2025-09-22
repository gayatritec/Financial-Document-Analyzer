# mongo_storage.py
"""MongoDB storage for financial analysis results."""

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from typing import Optional, List, Dict, Any
from conf import settings


class MongoStorage:
    def __init__(self):
        # Connect to MongoDB using server API v1 (works with Atlas)
        self.client = MongoClient(settings.MONGO_URI, server_api=ServerApi("1"))
        # Database name (you can change)
        self.db = self.client["financial_analyzer"]
        # Collection name
        self.collection = self.db["results"]

        # Optional: create an index on session_id for faster lookups and uniqueness
        try:
            self.collection.create_index("session_id", unique=True)
        except Exception:
            # index creation isn't critical at runtime; ignore errors here
            pass

    def save_result(self, session_id: str, query: str, output: str, filename: str) -> str:
        """
        Save the analysis result document and return the inserted_id as string.
        If a document with the same session_id already exists, this will insert another doc.
        """
        document = {
            "session_id": session_id,
            "query": query,
            "filename": filename,
            "output": output,
            "created_at": datetime.utcnow(),
        }
        result = self.collection.insert_one(document)
        return str(result.inserted_id)

    def get_result(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Return a single result document by session_id, or None if not found."""
        doc = self.collection.find_one({"session_id": session_id})
        if not doc:
            return None
        # Convert ObjectId to string for JSON serialization
        doc["_id"] = str(doc["_id"])
        # Convert datetimes to ISO strings for JSON friendliness
        if "created_at" in doc and hasattr(doc["created_at"], "isoformat"):
            doc["created_at"] = doc["created_at"].isoformat() + "Z"
        return doc

    def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Return a list of result documents sorted by created_at desc (limited)."""
        cursor = self.collection.find({}).sort("created_at", -1).limit(limit)
        docs = []
        for d in cursor:
            d["_id"] = str(d["_id"])
            if "created_at" in d and hasattr(d["created_at"], "isoformat"):
                d["created_at"] = d["created_at"].isoformat() + "Z"
            docs.append(d)
        return docs


# Single global instance for easy import
mongo_storage = MongoStorage()
