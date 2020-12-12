import json
from abc import abstractmethod
from dataclasses import dataclass
from typing import List


class Event:

    @abstractmethod
    def to_dict(self) -> dict:
        ...

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class StartVMs(Event):
    vms: List[str]
    user_id: str

    def to_dict(self) -> dict:
        return {
            'vms': self.vms,
            'user_id': self.user_id
        }