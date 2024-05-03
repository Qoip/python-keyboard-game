import pygame
from typing import Dict, Tuple

from bin.graph import Graph
from bin.view_constants import DEFAULT_COLOR, BACKGROUND_COLOR, CONTRAST_COLOR, GRAPH_OFFSET, MIN_WIGTH, \
    TYPING_HEIGHT, FONT, FONT_SIZE


class View:
    def __init__(self, color_scheme: Dict[str, Tuple[int, int, int]],
                 graph: Graph):
        self.color_scheme = color_scheme
        self.graph = graph
        self.words = []

        pygame.init()
        self.window_size = (max(graph.bounds[0] + GRAPH_OFFSET * 2, MIN_WIGTH),
                            graph.bounds[1] + GRAPH_OFFSET * 2 + TYPING_HEIGHT)
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Game")

        self.graph_start_point = (GRAPH_OFFSET, GRAPH_OFFSET)
        if MIN_WIGTH > graph.bounds[0] + GRAPH_OFFSET * 2:  # center the graph
            self.graph_start_point = (MIN_WIGTH // 2 - graph.bounds[0] // 2, GRAPH_OFFSET)

    def update(self):
        ''' Update the display '''
        self.screen.fill(BACKGROUND_COLOR)

        self.__draw_graph()
        pygame.draw.line(self.screen, CONTRAST_COLOR,
                         (0, self.window_size[1] - TYPING_HEIGHT),
                         (self.window_size[0], self.window_size[1] - TYPING_HEIGHT), 2)  # blocks dividor
        self.__draw_typing_block()

        pygame.display.flip()

    def __draw_graph(self):
        for edge in self.graph.edges:
            start = (self.graph.vertices[edge[0]].x + self.graph_start_point[0],
                     self.graph.vertices[edge[0]].y + self.graph_start_point[1])
            end = (self.graph.vertices[edge[1]].x + self.graph_start_point[0],
                   self.graph.vertices[edge[1]].y + self.graph_start_point[1])
            color = DEFAULT_COLOR
            if self.graph.vertices[edge[0]].owner == self.graph.vertices[edge[1]].owner:
                color = self.color_scheme.get(self.graph.vertices[edge[0]].owner, DEFAULT_COLOR)
            pygame.draw.line(self.screen, color, start, end, 2)

        for vertex in self.graph.vertices:
            owner = vertex.owner
            color = self.color_scheme.get(owner, DEFAULT_COLOR)
            if vertex.is_main:
                pygame.draw.circle(
                    self.screen, CONTRAST_COLOR,
                    (vertex.x + self.graph_start_point[0],
                     vertex.y + self.graph_start_point[1]),
                    vertex.size + 2, 2)
            pygame.draw.circle(self.screen, color,
                               (vertex.x + self.graph_start_point[0],
                                vertex.y + self.graph_start_point[1]),
                               vertex.size)

    def __draw_typing_block(self):
        ''' Draw typing block '''
        line = ""
        next_line_y = self.window_size[1] - TYPING_HEIGHT + 5
        for word in self.words:
            oldline = line
            line += f"{word} "
            width, _ = pygame.font.SysFont(FONT, FONT_SIZE).size(line)
            if width > self.window_size[0]:
                text = pygame.font.SysFont(FONT, FONT_SIZE).render(oldline, 1, CONTRAST_COLOR)
                self.screen.blit(text, (5, next_line_y))
                next_line_y += FONT_SIZE + 5
                line = f"{word} "
            print(word, next_line_y, line)
            if next_line_y > self.window_size[1]:
                break
        if next_line_y < self.window_size[1]:
            text = pygame.font.SysFont(FONT, FONT_SIZE).render(line, 1, CONTRAST_COLOR)
            self.screen.blit(text, (5, next_line_y))

    def run(self):
        ''' Run the game '''
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if len(self.words) > 0 and len(self.words[0]) > 0 and event.unicode == self.words[0][0]:
                        self.words[0] = self.words[0][1:]
                        if len(self.words[0]) == 0:
                            self.words.pop(0)

            self.update()
            pygame.time.Clock().tick(20)

        pygame.quit()
