# unibase/db/sql.py

from .base import BaseDatabase

class SQLDatabase(BaseDatabase):
    def connect(self):
        return f"Connected to SQL at {self.host}:{self.port}"

    def execute_query(self, query):
        return f"SQL executed query: {query}"

def connect(host, port, user, password):
    db = SQLDatabase(host, port, user, password)
    db.connect()
    return db

def execute_query(query):
    db = SQLDatabase("localhost", "3306", "user", "password")
    return db.execute_query(query)

def from_registry(info):
    return SQLDatabase.from_registry(info)
