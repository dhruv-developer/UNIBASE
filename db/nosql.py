# unibase/db/nosql.py

from .base import BaseDatabase

class NoSQLDatabase(BaseDatabase):
    def connect(self):
        return f"Connected to NoSQL at {self.host}:{self.port}"

    def execute_query(self, query):
        return f"NoSQL executed query: {query}"

def connect(host, port, user, password):
    db = NoSQLDatabase(host, port, user, password)
    db.connect()
    return db

def execute_query(query):
    db = NoSQLDatabase("localhost", "27017", "user", "password")
    return db.execute_query(query)

def from_registry(info):
    return NoSQLDatabase.from_registry(info)
