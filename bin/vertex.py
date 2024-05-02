''' Vertex class represents points on game field.'''


class Vertex:
    def __init__(self, x: int, y: int, owner: str | None = None, is_main: bool = False, size: int = 5, hp: int = 10):
        self.x = x
        self.y = y
        self.owner = owner
        self.is_main = is_main
        self.size = size
        self.hp = hp
        self.name: str = "no name"

    def __str__(self):
        return f"vertex ({self.x}, {self.y}), owned by {self.owner} ({self.is_main}), size: {self.size}, hp: {self.hp}"
