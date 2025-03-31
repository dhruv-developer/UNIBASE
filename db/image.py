# unibase/db/image.py

from .base import BaseDatabase

class ImageDatabase(BaseDatabase):
    def connect(self):
        return f"Connected to Image Storage at {self.host}:{self.port}"

    def execute_query(self, query):
        return f"Image DB executed query: {query}"

def connect(host, port, user, password):
    db = ImageDatabase(host, port, user, password)
    db.connect()
    return db

def execute_query(query):
    db = ImageDatabase("localhost", "9000", "user", "password")
    return db.execute_query(query)

def from_registry(info):
    return ImageDatabase.from_registry(info)
