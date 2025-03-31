# unibase/db/vector.py

from .base import BaseDatabase

class VectorDatabase(BaseDatabase):
    def connect(self):
        return f"Connected to Vector DB at {self.host}:{self.port}"

    def execute_query(self, query):
        return f"Vector DB executed query: {query}"

def connect(host, port, user, password):
    db = VectorDatabase(host, port, user, password)
    db.connect()
    return db

def execute_query(query):
    db = VectorDatabase("localhost", "1234", "user", "password")
    return db.execute_query(query)

def from_registry(info):
    return VectorDatabase.from_registry(info)
