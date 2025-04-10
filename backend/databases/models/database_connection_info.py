from dataclasses import dataclass

from sqlalchemy import create_engine


@dataclass
class DatabaseConnectionInfo:
    database_type: str
    host: str
    port: int
    user: str
    password: str
    name: str

    def to_sqlalchemy_engine(self):
        return create_engine(self._build_url())

    def _build_url(self) -> str:
        match self.database_type:
            case 'postgresql':
                return (
                    f'postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}'
                )
            case 'sqlite':
                return f'sqlite:///{self.name}'
            case _:
                raise ValueError(f'Unsupported database type: {self.database_type}')
