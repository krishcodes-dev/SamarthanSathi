import uuid
from sqlalchemy import String

def UUID_STR():
    """
    SQLite-safe UUID column.
    Stored as string but generated as uuid4.
    """
    return String(36)

def generate_uuid():
    return str(uuid.uuid4())
