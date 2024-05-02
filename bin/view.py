import pygame
from typing import Dict, Tuple

from bin.graph import Graph


class View:
    def __init__(self, color_scheme: Dict[str, Tuple[int, int, int]], graph: Graph):
        self.color_scheme = color_scheme
        self.graph = graph

        pygame.init()
        self.screen = pygame.display.set_mode((500, 500))
        pygame.display.set_caption("Game")

    def update(self):
        ''' Update the display '''
        self.screen.fill((255, 255, 255))

        for edge in self.graph.edges:
            start = (self.graph.vertices[edge[0]].x, self.graph.vertices[edge[0]].y)
            end = (self.graph.vertices[edge[1]].x, self.graph.vertices[edge[1]].y)
            color = (100, 100, 100)
            if self.graph.vertices[edge[0]].owner == self.graph.vertices[edge[1]].owner:
                color = self.color_scheme.get(self.graph.vertices[edge[0]].owner, (100, 100, 100))
            pygame.draw.line(self.screen, color, start, end, 2)

        for vertex in self.graph.vertices:
            owner = vertex.owner
            color = self.color_scheme.get(owner, (100, 100, 100))
            pygame.draw.circle(self.screen, color, (vertex.x, vertex.y), 10)

        pygame.display.flip()

    def run(self):
        ''' Run the game '''
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.update()

        pygame.quit()
