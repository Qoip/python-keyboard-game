""" View module for the game client. """

import pygame
from typing import Dict, Tuple, Literal, List
import queue

from bin.graph import Graph
from bin.view_constants import DEFAULT_COLOR, BACKGROUND_COLOR, CONTRAST_COLOR, GRAPH_OFFSET, MIN_WIGTH, \
    TYPING_HEIGHT, FONT, FONT_SIZE, HINT_FONT, HINT_FONT_SIZE, LEGEND_WIDTH, LEGEND_FONT, LEGEND_FONT_SIZE


class View:
    def __init__(self, color_scheme: Dict[str, Tuple[int, int, int]],
                 graph: Graph, name: str = "", legend: Dict[str, int] = {}):
        self.color_scheme: Dict[str, Tuple[int, int, int]] = color_scheme
        self.graph: Graph = graph
        self.legend: Dict[str, int] = legend
        self.words: List[str] = []

        self.events: queue.Queue = queue.Queue()

        self.new_graph: Graph = None
        self.stopped: bool = False
        self.__need_stop: bool = False

        self.my_name: str = name
        self.current_vertex: str = None
        for vertex in self.graph.vertices:  # set current vertex to mains
            if vertex.owner == name and vertex.is_main:
                self.current_vertex = vertex.name
                break
        assert self.current_vertex is not None, "No main vertex for player"

        self.mode: Literal["choose", "default", "viewer"] = "default"

        pygame.init()
        self.window_size = (max(graph.bounds[0] + GRAPH_OFFSET * 2 + LEGEND_WIDTH, MIN_WIGTH),
                            max(graph.bounds[1] + GRAPH_OFFSET * 2, (LEGEND_FONT_SIZE + 5) * 5) + TYPING_HEIGHT)
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Game")

        self.graph_start_point = (GRAPH_OFFSET, GRAPH_OFFSET)
        if MIN_WIGTH > graph.bounds[0] + GRAPH_OFFSET * 2:  # center the graph
            self.graph_start_point = (MIN_WIGTH // 2 - graph.bounds[0] // 2, GRAPH_OFFSET)

    def stop(self):
        ''' Stop the game '''
        self.__need_stop = True

    def resume(self):
        ''' Resume updates '''
        self.stopped = False

    def update(self):
        ''' Update the display '''
        self.screen.fill(BACKGROUND_COLOR)

        if self.new_graph:
            self.graph = self.new_graph
            self.new_graph = None
        self.__draw_graph()
        pygame.draw.line(self.screen, CONTRAST_COLOR,
                         (0, self.window_size[1] - TYPING_HEIGHT),
                         (self.window_size[0], self.window_size[1] - TYPING_HEIGHT), 2)  # blocks dividor
        self.__draw_typing_block()
        pygame.draw.line(self.screen, CONTRAST_COLOR,
                         (self.window_size[0] - LEGEND_WIDTH, 0),
                         (self.window_size[0] - LEGEND_WIDTH, self.window_size[1] - TYPING_HEIGHT), 2)  # legend dividor
        self.__draw_legend()
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

        for i, vertex in enumerate(self.graph.vertices):
            owner = vertex.owner
            color = self.color_scheme.get(owner, DEFAULT_COLOR)
            if vertex.is_main:
                pygame.draw.circle(
                    self.screen, CONTRAST_COLOR,
                    (vertex.x + self.graph_start_point[0],
                     vertex.y + self.graph_start_point[1]),
                    vertex.size, 3)  # main vertex border
                if self.mode == "default":  # owner hint needed
                    hint = pygame.font.SysFont(
                        HINT_FONT, HINT_FONT_SIZE, True).render(
                        vertex.owner, 1, CONTRAST_COLOR)
                    self.screen.blit(hint, (vertex.x + self.graph_start_point[0] - hint.get_width() // 2,
                                            vertex.y + self.graph_start_point[1] + vertex.size))
            pygame.draw.circle(self.screen, color,
                               (vertex.x + self.graph_start_point[0],
                                vertex.y + self.graph_start_point[1]),
                               vertex.size - (2 if vertex.is_main else 0))
            if self.mode == "choose" and self.graph.reachable(self.my_name, i) and not vertex.is_main:  # name hint
                hint = pygame.font.SysFont(
                    HINT_FONT, HINT_FONT_SIZE, True).render(
                    vertex.name, 1, CONTRAST_COLOR, BACKGROUND_COLOR)
                self.screen.blit(hint, (vertex.x + self.graph_start_point[0] - hint.get_width() // 2,
                                        vertex.y + self.graph_start_point[1] + vertex.size))
            elif self.mode == "default" and vertex.hp >= 0:  # hp hint
                hint = pygame.font.SysFont(
                    HINT_FONT, HINT_FONT_SIZE).render(
                    str(vertex.hp), 1, CONTRAST_COLOR, BACKGROUND_COLOR)
                self.screen.blit(hint, (vertex.x + self.graph_start_point[0] - hint.get_width() // 2,
                                        vertex.y + self.graph_start_point[1] - vertex.size - hint.get_height()))

            if vertex.name == self.current_vertex:  # current vertex border
                pygame.draw.rect(self.screen, CONTRAST_COLOR,
                                 (vertex.x + self.graph_start_point[0] - vertex.size - 4,
                                  vertex.y + self.graph_start_point[1] - vertex.size - 4,
                                  vertex.size * 2 + 8, vertex.size * 2 + 8), 2)

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
            if next_line_y > self.window_size[1]:
                break
        if next_line_y < self.window_size[1]:
            text = pygame.font.SysFont(FONT, FONT_SIZE).render(line, 1, CONTRAST_COLOR)
            self.screen.blit(text, (5, next_line_y))

    def __draw_legend(self):
        ''' Draw legend '''
        legend_start_point = (self.window_size[0] - LEGEND_WIDTH + 5, 5)
        for i, (key, value) in enumerate(self.legend.items()):
            color = self.color_scheme.get(key, DEFAULT_COLOR)
            text = pygame.font.SysFont(LEGEND_FONT, LEGEND_FONT_SIZE).render(f"{key}: {value}", 1, color)
            shadow = pygame.font.SysFont(LEGEND_FONT, LEGEND_FONT_SIZE).render(f"{key}: {value}", 1, CONTRAST_COLOR)
            self.screen.blit(shadow, (legend_start_point[0] + 1,
                             legend_start_point[1] + i * (LEGEND_FONT_SIZE + 5) + 1))
            self.screen.blit(shadow, (legend_start_point[0] - 1,
                             legend_start_point[1] + i * (LEGEND_FONT_SIZE + 5) + 1))
            self.screen.blit(shadow, (legend_start_point[0] + 1,
                             legend_start_point[1] + i * (LEGEND_FONT_SIZE + 5) - 1))
            self.screen.blit(shadow, (legend_start_point[0] - 1,
                             legend_start_point[1] + i * (LEGEND_FONT_SIZE + 5) - 1))
            self.screen.blit(text, (legend_start_point[0], legend_start_point[1] + i * (LEGEND_FONT_SIZE + 5)))

    def run(self) -> None:
        ''' Run the game '''
        running = True
        self.clock = pygame.time.Clock()
        while running:
            if self.__need_stop:
                self.stopped = True
                self.__need_stop = False
            if self.stopped:
                self.clock.tick(20)
                continue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:  # change mode
                        if self.mode == "default":
                            self.mode = "choose"
                            self.words = [""]
                        elif self.mode == "choose":
                            self.mode = "default"
                        break
                    if self.mode == "default":
                        if len(self.words) > 0 and len(self.words[0]) > 0 and event.unicode == self.words[0][0]:
                            self.words[0] = self.words[0][1:]
                            if len(self.words[0]) == 0:
                                self.words.pop(0)
                                self.events.put(("attack", self.current_vertex))
                    elif self.mode == "choose":
                        if event.unicode.isalpha():
                            self.words[0] += event.unicode
                            if len(self.words[0]) > 15:
                                self.words[0] = self.words[0][:15]
                        elif event.key == pygame.K_BACKSPACE and len(self.words[0]) > 0:
                            self.words[0] = self.words[0][:-1]
                        elif event.key == pygame.K_RETURN:
                            if any([self.graph.vertices[i].name == self.words[0] and self.graph.reachable(
                                    self.my_name, i) for i in range(len(self.graph.vertices))]):
                                self.current_vertex = self.words[0]
                                self.words = []
                                self.events.put(("change", self.current_vertex))
                                self.mode = "default"
                            else:
                                print("No such vertex to go.")  # TODO alert

            self.update()
            self.clock.tick(20)

        pygame.quit()
