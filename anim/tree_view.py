from dataclasses import dataclass

from manim import (
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

    leaf_order: list[int] = []
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


class HistoryTreeView:
    def __init__(self, layout: HistoryLayout):
        self.layout = layout
        count = max(layout.n, 1)
        spacing = theme.LEAF_SPACING
        if (count - 1) * spacing > theme.TREE_MAX_WIDTH:
            spacing = theme.TREE_MAX_WIDTH / (count - 1)
        self.spacing = spacing
        self.center_slot = (count - 1) / 2
        self.nodes: dict[int, VGroup] = {}
        self.edges: dict[int, Line] = {}
        self.touched_nodes: set[int] = set()
        self.touched_edges: set[int] = set()

    def point(self, v: int) -> np.ndarray:
        x = (self.layout.slot[v] - self.center_slot) * self.spacing
        y = theme.TREE_BOTTOM + self.layout.height[v] * theme.LEVEL_HEIGHT
        return np.array([x, y, 0.0])

    def make_leaf(self, v: int) -> VGroup:
        circle = Circle(radius=theme.NODE_RADIUS)
        circle.set_stroke(theme.LEAF_STROKE, width=theme.NODE_STROKE)
        circle.set_fill(theme.LEAF_FILL, opacity=theme.LEAF_FILL_OPACITY)
        label = MathTex(str(v), font_size=theme.LABEL_SIZE)
        node = VGroup(circle, label).move_to(self.point(v))
        self.nodes[v] = node
        return node

    def make_union(self, v: int) -> VGroup:
        circle = Circle(radius=theme.NODE_RADIUS)
        circle.set_stroke(theme.UNION_STROKE, width=theme.NODE_STROKE)
        circle.set_fill(theme.BACKGROUND, opacity=1)
        label = MathTex(f"t{{=}}{self.layout.time[v]}", font_size=theme.UNION_LABEL_SIZE)
        label.set_color(theme.UNION_STROKE)
        if label.width > 1.6 * theme.NODE_RADIUS:
            label.scale_to_fit_width(1.6 * theme.NODE_RADIUS)
        node = VGroup(circle, label).move_to(self.point(v))
        self.nodes[v] = node
        return node

    def make_edge(self, child: int, parent: int) -> Line:
        edge = Line(self.point(child), self.point(parent), buff=theme.NODE_RADIUS)
        edge.set_stroke(theme.EDGE_COLOR, width=theme.EDGE_STROKE, opacity=theme.EDGE_OPACITY)
        self.edges[child] = edge
        return edge

    def leaves(self) -> list[VGroup]:
        return [self.make_leaf(v) for v in self.layout.leaf_order]

    def base_stroke(self, v: int):
        return theme.LEAF_STROKE if v <= self.layout.n else theme.UNION_STROKE

    def highlight(self, v: int, color) -> Animation:
        self.touched_nodes.add(v)
        return self.nodes[v][0].animate.set_stroke(color, width=theme.HIGHLIGHT_STROKE)

    def highlight_edge(self, child: int, color) -> Animation:
        self.touched_edges.add(child)
        return self.edges[child].animate.set_stroke(color, width=2 * theme.EDGE_STROKE, opacity=1)

    def reset(self) -> list[Animation]:
        animations = [
            self.nodes[v][0].animate.set_stroke(self.base_stroke(v), width=theme.NODE_STROKE)
            for v in sorted(self.touched_nodes)
        ]
        animations += [
            self.edges[c].animate.set_stroke(
                theme.EDGE_COLOR, width=theme.EDGE_STROKE, opacity=theme.EDGE_OPACITY
            )
            for c in sorted(self.touched_edges)
        ]
        self.touched_nodes.clear()
        self.touched_edges.clear()
        return animations
