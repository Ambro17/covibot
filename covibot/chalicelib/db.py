from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class User:
    id: str
    username: str


class Repository(ABC):

    @abstractmethod
    def get_user(self, user_id) -> User:
        ...

    @abstractmethod
    def reservar(self) -> bool:
        ...

    @abstractmethod
    def list_reservas(self) -> List[User]:
        ...




class DynamoDBPersistence(Repository):
    pass
