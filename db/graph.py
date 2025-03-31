# unibase/db/graph.py

from .base import BaseDatabase

class GraphDatabase(BaseDatabase):
    def connect(self):
        return f"Connected to Graph DB at {self.host}:{self.port}"

    def execute_query(self, query):
        return f"Graph DB executed query: {query}"

def connect(host, port, user, password):
    db = GraphDatabase(host, port, user, password)
    db.connect()
    return db

def execute_query(query):
    db = GraphDatabase("localhost", "7687", "user", "password")
    return db.execute_query(query)

def from_registry(info):
    return GraphDatabase.from_registry(info)
