from manim import (
    DOWN,
    UP,
    Animation,
    FadeIn,
    Line,
    MathTex,
    RoundedRectangle,
    Text,
    Transform,
    VGroup,
    np,
)

import theme
from tree_view import HistoryLayout

EMPTY = "\\cdot"


class DsuPanel:
    def __init__(self, init_event: dict, layout: HistoryLayout, center: np.ndarray):
        self.n = init_event["n"]
        self.layout = layout
        self.center = center
        rows = self.n + 1
        self.row_height = min(theme.PANEL_ROW_HEIGHT, theme.PANEL_MAX_HEIGHT / rows)
        self.columns = [-theme.PANEL_COL_GAP, 0.0, theme.PANEL_COL_GAP]
        self.cells: dict[tuple[int, int], MathTex] = {}
        self.highlighted: set[tuple[int, int]] = set()

        top = center[1] + (rows - 1) * self.row_height / 2
        self.top = top
        header = VGroup(
            Text("x", font_size=theme.PANEL_HEADER_SIZE, color=theme.SECONDARY),
            Text("padre[x]", font_size=theme.PANEL_HEADER_SIZE, color=theme.SECONDARY),
            Text("nodo[x]", font_size=theme.PANEL_HEADER_SIZE, color=theme.SECONDARY),
        )
        for col, mob in enumerate(header):
            mob.move_to(self.slot(0, col))
        self.header = header

        self.node_values: dict[int, int | None] = {x: init_event["compNode"][x - 1] for x in range(1, self.n + 1)}
        body = VGroup()
        for x in range(1, self.n + 1):
            for col, value in enumerate((x, init_event["dsuParent"][x - 1], init_event["compNode"][x - 1])):
                cell = self.make_cell(x, col, value)
                self.cells[(x, col)] = cell
                body.add(cell)
        self.body = body

        rule_y = top - self.row_height / 2
        width = 2 * theme.PANEL_COL_GAP + 1.4
        self.rule = Line(
            np.array([center[0] - width / 2 + 0.15, rule_y, 0]),
            np.array([center[0] + width / 2 - 0.15, rule_y, 0]),
        ).set_stroke(theme.SECONDARY, width=1.5)
        height = rows * self.row_height + 0.3
        self.frame = RoundedRectangle(width=width, height=height, corner_radius=0.15)
        self.frame.set_stroke(theme.SECONDARY, width=1.5).move_to(center)
        self.title = Text("DSU auxiliar", font_size=theme.PANEL_TITLE_SIZE, color=theme.DETAIL)
        self.title.next_to(self.frame, UP, buff=0.15)
        self.group = VGroup(self.title, self.frame, self.rule, self.header, self.body)

    def slot(self, row: int, col: int) -> np.ndarray:
        return np.array([self.center[0] + self.columns[col], self.top - row * self.row_height, 0.0])

    def node_tex(self, value: int | None) -> MathTex:
        if value is None:
            return MathTex(EMPTY, font_size=theme.PANEL_CELL_SIZE, color=theme.SECONDARY)
        if value <= self.n:
            return MathTex(str(value), font_size=theme.PANEL_CELL_SIZE, color=theme.TEXT_COLOR)
        return MathTex(f"t{{=}}{self.layout.time[value]}", font_size=theme.PANEL_CELL_SIZE, color=theme.UNION_STROKE)

    def make_cell(self, x: int, col: int, value: int | None) -> MathTex:
        if col == 2:
            tex = self.node_tex(value)
        else:
            color = theme.SECONDARY if col == 0 else theme.TEXT_COLOR
            tex = MathTex(str(value), font_size=theme.PANEL_CELL_SIZE, color=color)
        return tex.move_to(self.slot(x, col))

    def appear(self) -> Animation:
        return FadeIn(self.group, shift=DOWN * 0.1)

    def mark(self, x: int, color, cols=(0, 1)) -> list[Animation]:
        animations = []
        for col in cols:
            self.highlighted.add((x, col))
            animations.append(self.cells[(x, col)].animate.set_color(color))
        return animations

    def set_parent(self, x: int, value: int) -> Animation:
        new = self.make_cell(x, 1, value).set_color(theme.ACCENT)
        self.highlighted.add((x, 1))
        return Transform(self.cells[(x, 1)], new)

    def set_node(self, x: int, value: int | None) -> Animation:
        self.node_values[x] = value
        self.highlighted.discard((x, 2))
        new = self.make_cell(x, 2, value)
        return Transform(self.cells[(x, 2)], new)

    def base_color(self, x: int, col: int):
        if col == 0:
            return theme.SECONDARY
        if col == 1:
            return theme.TEXT_COLOR
        value = self.node_values[x]
        if value is None:
            return theme.SECONDARY
        return theme.TEXT_COLOR if value <= self.n else theme.UNION_STROKE

    def reset(self) -> list[Animation]:
        animations = []
        for x, col in sorted(self.highlighted):
            animations.append(self.cells[(x, col)].animate.set_color(self.base_color(x, col)))
        self.highlighted.clear()
        return animations
