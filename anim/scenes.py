from manim import DL, DOWN, DR, LEFT, RIGHT, Circle, Scene, Text, VGroup

import theme
from captions import Captions
from player import TracePlayer
from trace_loader import load_trace
from tree_view import HistoryTreeView, history_layout


def source_footer() -> Text:
    footer = Text("trazas generadas por dsu_tree.cpp", font_size=theme.FOOTER_SIZE, color=theme.SECONDARY)
    return footer.to_corner(DL, buff=0.35)


def legend() -> VGroup:
    def entry(stroke, fill, opacity, text):
        dot = Circle(radius=0.12).set_stroke(stroke, width=3).set_fill(fill, opacity=opacity)
        label = Text(text, font_size=theme.FOOTER_SIZE, color=theme.SECONDARY)
        return VGroup(dot, label.next_to(dot, RIGHT, buff=0.15))

    items = VGroup(
        entry(theme.LEAF_STROKE, theme.LEAF_FILL, theme.LEAF_FILL_OPACITY, "elemento"),
        entry(theme.UNION_STROKE, theme.BACKGROUND, 1, "nodo de unión (momento t)"),
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
    return items.to_corner(DR, buff=0.35)


class TraceScene(Scene):
    SCENARIO = "demo"

    def setup(self):
        self.camera.background_color = theme.BACKGROUND
        self.events = load_trace(self.SCENARIO)
        self.view = HistoryTreeView(history_layout(self.events))
        self.captions = Captions()
        self.player = TracePlayer(self, self.view, self.captions)
        self.add(source_footer(), legend())


class DemoUniones(TraceScene):
    SCENARIO = "demo"

    def construct(self):
        self.player.run(self.events)
        self.player.play(*self.captions.clear(), *self.view.reset())
        self.wait(1)


class CasosBorde(TraceScene):
    SCENARIO = "bordes"

    def construct(self):
        self.player.run(self.events)
        self.player.play(*self.captions.clear(), *self.view.reset())
        self.wait(1)
