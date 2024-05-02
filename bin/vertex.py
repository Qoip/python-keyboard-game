''' Vertex class represents points on game field.'''


class Vertex:
    def __init__(self, x: int, y: int, owner: str | None = None, is_main: bool = False):
        self.x = x
        self.y = y
        self.owner = owner
        self.is_main = is_main

    def __str__(self):
        return f"vertex at ({self.x}, {self.y}), owned by {self.owner}"
