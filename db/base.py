# unibase/db/base.py

class BaseDatabase:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port if port is not None else "default_port"
        self.user = user
        self.password = password
        self.active = True
        self.data = []  # In‑memory data store

    def connect(self):
        raise NotImplementedError("Connect method not implemented.")

    def execute_query(self, query):
        raise NotImplementedError("Query execution not implemented.")

    def insert(self, record: dict):
        if not self.active:
            raise Exception("Database is deactivated")
        self.data.append(record)
        return f"Record inserted into {self.__class__.__name__}"

    def query(self, query_text: str):
        if query_text.strip().lower() == "select *":
            return self.data
        if "=" in query_text:
            key, value = query_text.split("=", 1)
            key = key.strip()
            value = value.strip()
            return [record for record in self.data if str(record.get(key)) == value]
        return f"{self.__class__.__name__} executed query: {query_text}"

    def delete(self, key, value):
        if not self.active:
            raise Exception("Database is deactivated")
        original_count = len(self.data)
        self.data = [r for r in self.data if str(r.get(key)) != value]
        deleted_count = original_count - len(self.data)
        return f"Deleted {deleted_count} records from {self.__class__.__name__}"

    def update(self, key, value, update_data: dict):
        if not self.active:
            raise Exception("Database is deactivated")
        updated_count = 0
        for i, record in enumerate(self.data):
            if str(record.get(key)) == value:
                self.data[i].update(update_data)
                updated_count += 1
        return f"Updated {updated_count} records in {self.__class__.__name__}"

    def deactivate(self):
        self.active = False
        return f"{self.__class__.__name__} has been deactivated."

    def download(self):
        return self.data

    def __str__(self):
        return f"{self.__class__.__name__}({self.host}:{self.port}, active={self.active})"

    @classmethod
    def from_registry(cls, info):
        instance = cls(info.get("host", "localhost"),
                       info.get("port", "default_port"),
                       info.get("user", "user"),
                       info.get("password", "password"))
        instance.active = info.get("active", True)
        instance.data = info.get("data", [])
        return instance
