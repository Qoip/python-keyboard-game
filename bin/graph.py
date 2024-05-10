from typing import List, Tuple, Dict, Any
from random import randrange
from bin.vertex import Vertex


class Graph:
    def __init__(self):
        self.vertices: List[Vertex] = []
        self.edges: List[Tuple[int, int]] = []
        self.bounds: Tuple[int, int] = (0, 0)
        self.dense: int = 0  # dense shows how many vertices for each player there are

    def generate(self, nicknames: List[str], bounds: Tuple[int, int] = (500, 500), dense: int = 3) -> None:
        ''' Generate graph '''
        assert len(nicknames) <= 4, "Too many players"
        vertices_count = len(nicknames) * (dense + 1)
        self.bounds = bounds
        self.dense = dense

        start_points = self.__get_start_points(len(nicknames))
        self.vertices = [
            Vertex(start_points[i][0], start_points[i][1], nicknames[i], True, -1) for i in range(len(nicknames))
        ]
        while len(self.vertices) < vertices_count:
            point = self.__get_best_point(bounds)
            self.vertices.append(Vertex(point[0], point[1], None, False, randrange(5, 16)))  # add best with random size
        names = []
        with open('data/names.txt', 'r') as file:
            names = file.read().splitlines()
        for vertex in self.vertices:  # pick random names for vertices
            vertex.name = names.pop(randrange(len(names)))

        coefficient_range = [i / 20 for i in range(1, 20)]
        for coefficient in coefficient_range:
            for vertex in self.vertices:
                for other_vertex in self.vertices:
                    if vertex == other_vertex:
                        continue
                    if self.distance((vertex.x, vertex.y), (other_vertex.x, other_vertex.y)) < bounds[0] * coefficient:
                        self.edges.append((self.vertices.index(vertex), self.vertices.index(other_vertex)))
            if self.__graph_connected():
                break
            self.edges = []

    def __graph_connected(self) -> bool:
        ''' Check if graph is connected '''
        visited = [False for _ in range(len(self.vertices))]
        to_visit = [0]
        while to_visit:
            vertex = to_visit.pop()
            visited[vertex] = True
            for edge in self.edges:
                if vertex in edge:
                    next_vertex = edge[1] if edge[0] == vertex else edge[0]
                    if not visited[next_vertex]:
                        to_visit.append(next_vertex)
        return all(visited)

    def __get_start_points(self, count: int) -> List[Tuple[int, int]]:
        ''' Get start points '''
        start_points = [(randrange(0, self.bounds[0]),
                         randrange(0, self.bounds[1]))]
        if count == 2:
            start_points = [
                (randrange(0, int(self.bounds[0] * 0.1)),
                 randrange(0, self.bounds[1])),  # left side
                (randrange(
                    int(self.bounds[0] * 0.9), self.bounds[0]), randrange(0, self.bounds[1]))  # right side
            ]
        elif count == 3:
            start_points = [
                (randrange(0, int(self.bounds[0] * 0.1)),
                 randrange(0, int(self.bounds[1] * 0.1))),  # top left
                (randrange(int(self.bounds[0] * 0.9), self.bounds[0]),
                 randrange(0, int(self.bounds[1] * 0.1))),  # top right
                (randrange(int(self.bounds[0] * 0.45), int(self.bounds[0] * 0.55)),
                 randrange(int(self.bounds[1] * 0.9), self.bounds[1]))  # bottom center
            ]
        elif count == 4:
            start_points = [
                (randrange(0, int(self.bounds[0] * 0.1)),
                 randrange(0, int(self.bounds[1] * 0.1))),  # top left
                (randrange(int(self.bounds[0] * 0.9), self.bounds[0]),
                 randrange(0, int(self.bounds[1] * 0.1))),  # top right
                (randrange(0, int(self.bounds[0] * 0.1)), randrange(
                    int(self.bounds[1] * 0.9), self.bounds[1])),  # bottom left
                (randrange(int(self.bounds[0] * 0.9), self.bounds[0]), randrange(
                    int(self.bounds[1] * 0.9), self.bounds[1]))  # bottom right
            ]
        return start_points

    def __get_best_point(self, bounds: Tuple[int, int]) -> Tuple[int, int]:
        ''' Get the best point for new vertex '''
        points_rate: List[List[Tuple[int, int], int]] = []  # list of pairs (point, rate)
        for _ in range(1000):
            points_rate.append([(randrange(int(bounds[0] * 0.1), int(bounds[0] * 0.9)),
                                 randrange(int(bounds[1] * 0.1), int(bounds[1] * 0.9))), 0])
            for vertex in self.vertices:
                if self.distance((vertex.x, vertex.y), points_rate[-1][0]) < min(bounds) * 0.2:
                    points_rate[-1][1] += min(bounds) * 0.2 - self.distance((vertex.x, vertex.y), points_rate[-1][0])
        points_rate.sort(key=lambda x: x[1], reverse=True)
        return points_rate[-1][0]

    def distance(self, coordinate1: Tuple[int, int], coordinate2: Tuple[int, int]) -> float:
        ''' Calculate distance between two points '''
        return ((coordinate1[0] - coordinate2[0]) ** 2 + (coordinate1[1] - coordinate2[1]) ** 2) ** 0.5

    def connected(self, vertex1: int, vertex2: int) -> bool:
        ''' Check if two vertices are connected '''
        for edge in self.edges:
            if vertex1 in edge and vertex2 in edge:
                return True
        return False

    def reachable(self, name: str, vertex: int) -> bool:
        ''' Check if vertex is reachable by "name"'''
        for edge in self.edges:
            if vertex in edge and (self.vertices[edge[0]].owner == name or self.vertices[edge[1]].owner == name):
                return True
        return False

    def count(self, name: str) -> int:
        ''' Count vertices owned by "name" '''
        return len([vertex for vertex in self.vertices if vertex.owner == name])

    def get_main(self, name: str) -> int:
        ''' Get main vertex index of name'''
        for i, vertex in enumerate(self.vertices):
            if vertex.owner == name and vertex.is_main:
                return i
        return None

    def get_id(self, name: str) -> int:
        ''' Get vertex index by name '''
        for i, vertex in enumerate(self.vertices):
            if vertex.name == name:
                return i
        return None

    def to_dict(self) -> Dict[str, Any]:
        ''' Convert to dict '''
        return {
            "vertices": [vertex.to_dict() for vertex in self.vertices],
            "edges": self.edges,
            "bounds": self.bounds,
            "dense": self.dense
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        ''' Load from dict '''
        self.vertices = [Vertex().from_dict(vertex) for vertex in data["vertices"]]
        self.edges = data["edges"]
        self.bounds = data["bounds"]
        self.dense = data["dense"]
