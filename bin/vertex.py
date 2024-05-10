''' Vertex class represents points on game field.'''

from typing import Dict, Any


class Vertex:
    def __init__(self, x: int, y: int, owner: str | None = None, is_main: bool = False, size: int = 5,
                 name: str = "no name", hp: int = 10):
        self.x = x
        self.y = y
        self.owner = owner
        self.is_main = is_main
        self.size = size
        self.hp = hp
        self.name: str = name

    def __str__(self):
        return f"vertex ({self.x}, {self.y}), owned by {self.owner} ({self.is_main}), size: {self.size}, hp: {self.hp}"

    def to_dict(self) -> Dict[str, Any]:
        ''' Convert to dict '''
        return {
            "x": self.x,
            "y": self.y,
            "owner": self.owner,
            "is_main": self.is_main,
            "size": self.size,
            "hp": self.hp,
            "name": self.name
        }

    @classmethod
    def from_dict(self, data: Dict[str, Any]):
        ''' Load from dict '''
        self.x = data["x"]
        self.y = data["y"]
        self.owner = data["owner"]
        self.is_main = data["is_main"]
        self.size = data["size"]
        self.hp = data["hp"]
        self.name = data["name"]
