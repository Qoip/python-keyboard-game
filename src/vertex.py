''' Vertex class '''

from typing import Any, Dict


class Vertex:
    ''' Vertex class implementing point on graph with data '''
    def __init__(self, x: int, y: int, owner: str | None = None, is_main: bool = False, size: int = 5,
                 name: str = "no name", hp: int = 10):
        self.x: int = x
        self.y: int = y
        self.owner: str = owner
        self.is_main: bool = is_main
        self.size: int = size
        self.hp: int = hp
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
    def from_dict(cls, data: Dict[str, Any]) -> "Vertex":
        ''' Load from dict '''
        instance = cls(data['x'],
                       data['y'],
                       data['owner'],
                       data['is_main'],
                       data['size'],
                       data['name'],
                       data['hp'])
        return instance
