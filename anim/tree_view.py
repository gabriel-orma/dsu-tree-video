from dataclasses import dataclass, field

from manim import (
    RIGHT,
    Animation,
    Circle,
    Line,
    MathTex,
    VGroup,
    np,
)

import theme


@dataclass
class HistoryLayout:
    n: int
    leaf_order: list[int]
    slot: dict[int, float]
    height: dict[int, int]
    children: dict[int, tuple[int, int]]
    time: dict[int, int]


def history_layout(events: list[dict]) -> HistoryLayout:
    n = events[0]["n"]
    children: dict[int, tuple[int, int]] = {}
    time: dict[int, int] = {}
    for event in events:
        if event["op"] == "unite" and event["merged"]:
            left, right = event["children"]
            children[event["newNode"]] = (left, right)
            time[event["newNode"]] = event["t"]

    has_parent = {child for pair in children.values() for child in pair}
    nodes = list(range(1, n + 1)) + sorted(children)
    roots = [v for v in nodes if v not in has_parent]

    height: dict[int, int] = {}
    smallest_leaf: dict[int, int] = {}

    def visit(v: int) -> None:
        if v not in children:
            height[v] = 0
            smallest_leaf[v] = v
            return
        left, right = children[v]
        visit(left)
        visit(right)
        height[v] = max(height[left], height[right]) + 1
        smallest_leaf[v] = min(smallest_leaf[left], smallest_leaf[right])

    for root in roots:
        visit(root)

    leaf_order: list[int] = []

    def collect(v: int) -> None:
        if v not in children:
            leaf_order.append(v)
            return
        collect(children[v][0])
        collect(children[v][1])

    for root in sorted(roots, key=lambda r: smallest_leaf[r]):
        collect(root)

    slot: dict[int, float] = {leaf: float(i) for i, leaf in enumerate(leaf_order)}

    def place(v: int) -> float:
        if v not in slot:
            left, right = children[v]
            slot[v] = (place(left) + place(right)) / 2
        return slot[v]

    for root in roots:
        place(root)

    return HistoryLayout(n, leaf_order, slot, height, children, time)


@dataclass
class TreeBox:
    center_x: float = 0.0
    max_width: float = 11.5
    bottom: float = -2.6
    top: float = 2.2
    spacing: float = 1.5
    level: float = 1.3
    radius: float = theme.NODE_RADIUS
    show_ids: bool = False
    label_size: int = theme.LABEL_SIZE
    union_label_size: int = theme.UNION_LABEL_SIZE
    extra: dict = field(default_factory=dict)


class HistoryTreeView:
    def __init__(self, layout: HistoryLayout, box: TreeBox | None = None):
        self.layout = layout
        self.box = box or TreeBox()
        count = max(layout.n, 1)
        spacing = self.box.spacing
        if count > 1 and (count - 1) * spacing > self.box.max_width:
            spacing = self.box.max_width / (count - 1)
        self.spacing = spacing
        self.center_slot = (count - 1) / 2
        max_height = max(layout.height.values(), default=0)
        available = self.box.top - self.box.bottom
        self.level_height = self.box.level if max_height == 0 else min(self.box.level, available / max_height)
        self.bottom = self.box.bottom
        if max_height * self.level_height < available:
            self.bottom = self.box.bottom + (available - max_height * self.level_height) / 3
        self.nodes: dict[int, VGroup] = {}
        self.tags: dict[int, MathTex] = {}
        self.edges: dict[int, Line] = {}
        self.touched_nodes: set[int] = set()
        self.touched_edges: set[int] = set()

    @property
    def radius(self) -> float:
        return self.box.radius

    def point(self, v: int) -> np.ndarray:
        x = self.box.center_x + (self.layout.slot[v] - self.center_slot) * self.spacing
        y = self.bottom + self.layout.height[v] * self.level_height
        return np.array([x, y, 0.0])

    def is_leaf(self, v: int) -> bool:
        return v <= self.layout.n

    def time(self, v: int) -> int:
        return 0 if self.is_leaf(v) else self.layout.time[v]

    def short(self, v: int) -> str:
        if self.is_leaf(v) or self.box.show_ids:
            return str(v)
        return f"(t={self.layout.time[v]})"

    def make_leaf(self, v: int) -> VGroup:
        circle = Circle(radius=self.radius)
        circle.set_stroke(theme.LEAF_STROKE, width=theme.NODE_STROKE)
        circle.set_fill(theme.LEAF_FILL, opacity=theme.LEAF_FILL_OPACITY)
        label = MathTex(str(v), font_size=self.box.label_size)
        circle.set_z_index(1)
        label.set_z_index(2)
        node = VGroup(circle, label).move_to(self.point(v))
        self.nodes[v] = node
        return node

    def make_union(self, v: int) -> VGroup:
        circle = Circle(radius=self.radius)
        circle.set_stroke(theme.UNION_STROKE, width=theme.NODE_STROKE)
        circle.set_fill(theme.BACKGROUND, opacity=1)
        if self.box.show_ids:
            label = MathTex(str(v), font_size=self.box.label_size)
        else:
            label = MathTex(f"t{{=}}{self.layout.time[v]}", font_size=self.box.union_label_size)
            label.set_color(theme.UNION_STROKE)
        if label.width > 1.6 * self.radius:
            label.scale_to_fit_width(1.6 * self.radius)
        circle.set_z_index(1)
        label.set_z_index(2)
        node = VGroup(circle, label).move_to(self.point(v))
        self.nodes[v] = node
        return node

    def make_tag(self, v: int) -> MathTex:
        tag = MathTex(f"t{{=}}{self.layout.time[v]}", font_size=self.box.union_label_size, color=theme.UNION_STROKE)
        tag.next_to(self.point(v), RIGHT, buff=self.radius + 0.08)
        tag.set_z_index(2)
        self.tags[v] = tag
        return tag

    def make_edge(self, child: int, parent: int) -> Line:
        edge = Line(self.point(child), self.point(parent), buff=self.radius)
        edge.set_stroke(theme.EDGE_COLOR, width=theme.EDGE_STROKE, opacity=theme.EDGE_OPACITY)
        self.edges[child] = edge
        return edge

    def leaves(self) -> list[VGroup]:
        return [self.make_leaf(v) for v in self.layout.leaf_order]

    def base_stroke(self, v: int):
        return theme.LEAF_STROKE if self.is_leaf(v) else theme.UNION_STROKE

    def highlight(self, v: int, color) -> Animation:
        self.touched_nodes.add(v)
        return self.nodes[v][0].animate.set_stroke(color, width=theme.HIGHLIGHT_STROKE)

    def highlight_edge(self, child: int, color) -> Animation:
        self.touched_edges.add(child)
        return self.edges[child].animate.set_stroke(color, width=2 * theme.EDGE_STROKE, opacity=1)

    def reset(self, keep: tuple[int, ...] = ()) -> list[Animation]:
        kept = self.touched_nodes & set(keep)
        animations = [
            self.nodes[v][0].animate.set_stroke(self.base_stroke(v), width=theme.NODE_STROKE)
            for v in sorted(self.touched_nodes - kept)
        ]
        animations += [
            self.edges[c].animate.set_stroke(theme.EDGE_COLOR, width=theme.EDGE_STROKE, opacity=theme.EDGE_OPACITY)
            for c in sorted(self.touched_edges)
        ]
        self.touched_nodes = kept
        self.touched_edges.clear()
        return animations

    def everything(self) -> VGroup:
        return VGroup(*self.nodes.values(), *self.edges.values(), *self.tags.values())
