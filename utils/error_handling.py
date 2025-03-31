# unibase/utils/error_handling.py

class UnibaseError(Exception):
    """Base exception class for UNIBASE."""
    pass

class DatabaseConnectionError(UnibaseError):
    """Exception raised for database connection errors."""
    pass

class QueryExecutionError(UnibaseError):
    """Exception raised for query execution errors."""
    pass
