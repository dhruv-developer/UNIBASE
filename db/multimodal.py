# unibase/db/multimodal.py

from .base import BaseDatabase

class MultiModalDatabase(BaseDatabase):
    def connect(self):
        return f"Connected to Multi-Modal DB at {self.host}:{self.port}"

    def execute_query(self, query):
        return f"Multi-Modal DB executed query: {query}"

def connect(host, port, user, password):
    db = MultiModalDatabase(host, port, user, password)
    db.connect()
    return db

def execute_query(query):
    db = MultiModalDatabase("localhost", "5000", "user", "password")
    return db.execute_query(query)

def from_registry(info):
    return MultiModalDatabase.from_registry(info)
