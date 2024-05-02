import pygame
from typing import Dict, Tuple

from bin.graph import Graph
from bin.view_constants import DEFAULT_COLOR, BACKGROUND_COLOR, CONTRAST_COLOR


class View:
    def __init__(self, color_scheme: Dict[str, Tuple[int, int, int]],
                 graph: Graph, screen_size: Tuple[int, int] = (500, 500)):
        self.color_scheme = color_scheme
        self.graph = graph

        pygame.init()
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption("Game")

    def update(self):
        ''' Update the display '''
        self.screen.fill(BACKGROUND_COLOR)

        for edge in self.graph.edges:
            start = (self.graph.vertices[edge[0]].x, self.graph.vertices[edge[0]].y)
            end = (self.graph.vertices[edge[1]].x, self.graph.vertices[edge[1]].y)
            color = DEFAULT_COLOR
            if self.graph.vertices[edge[0]].owner == self.graph.vertices[edge[1]].owner:
                color = self.color_scheme.get(self.graph.vertices[edge[0]].owner, DEFAULT_COLOR)
            pygame.draw.line(self.screen, color, start, end, 2)

        for vertex in self.graph.vertices:
            owner = vertex.owner
            color = self.color_scheme.get(owner, DEFAULT_COLOR)
            if vertex.is_main:
                pygame.draw.circle(self.screen, CONTRAST_COLOR, (vertex.x, vertex.y), vertex.size + 2, 2)
            pygame.draw.circle(self.screen, color, (vertex.x, vertex.y), vertex.size, 0)

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
