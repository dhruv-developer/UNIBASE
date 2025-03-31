import os

class Config:
    SQL_HOST = os.getenv("SQL_HOST", "localhost")
    SQL_PORT = os.getenv("SQL_PORT", "3306")
    NOSQL_HOST = os.getenv("NOSQL_HOST", "localhost")
    NOSQL_PORT = os.getenv("NOSQL_PORT", "27017")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
