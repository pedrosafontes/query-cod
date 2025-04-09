from dataclasses import dataclass


@dataclass
class DatabaseConnectionInfo:
    database_type: str
    host: str
    port: int
    user: str
    password: str
    name: str
