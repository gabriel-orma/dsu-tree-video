from manim import (
    LEFT,
    RIGHT,
    Animation,
    FadeIn,
    LaggedStart,
    MathTex,
    Rectangle,
    Text,
    Transform,
    VGroup,
    np,
)

import theme


def value_tex(value: int, size: int, color) -> MathTex:
    return MathTex(str(value), font_size=size, color=color)


class ArrayRow:
    def __init__(
        self,
        name: str,
        values: list[int],
        left_x: float,
        y: float,
        cell_width: float = theme.CELL_WIDTH,
        cell_height: float = theme.CELL_HEIGHT,
        dim: list[bool] | None = None,
        color=theme.TEXT_COLOR,
        is_header: bool = False,
        text_size: int | None = None,
    ):
        self.values = list(values)
        self.dim = list(dim) if dim is not None else [False] * len(values)
        self.color = color
        self.is_header = is_header
        self.cell_width = cell_width
        self.left_x = left_x
        self.y = y
        self.size = text_size or theme.CELL_TEXT_SIZE
        self.label = Text(name, font=theme.MONO_FONT, font_size=theme.ROW_LABEL_SIZE, color=theme.DETAIL)
        self.label.move_to(np.array([left_x - 0.2, y, 0]), aligned_edge=RIGHT)
        self.boxes = VGroup()
        self.texts: list[MathTex] = []
        for i, value in enumerate(self.values):
            center = self.center(i)
            if not is_header:
                box = Rectangle(width=cell_width, height=cell_height)
                box.set_stroke(theme.SECONDARY, width=1.5).move_to(center)
                self.boxes.add(box)
            self.texts.append(self.make_text(i, value).move_to(center))
        self.marked: set[int] = set()
        self.group = VGroup(self.label, self.boxes, *self.texts)

    def center(self, i: int) -> np.ndarray:
        return np.array([self.left_x + (i + 0.5) * self.cell_width, self.y, 0.0])

    def text_color(self, i: int):
        if self.is_header:
            return theme.SECONDARY
        return theme.SECONDARY if self.dim[i] else self.color

    def make_text(self, i: int, value: int) -> MathTex:
        size = self.size if not self.is_header else round(self.size * 0.82)
        return value_tex(value, size, self.text_color(i))

    def appear(self) -> Animation:
        return LaggedStart(
            FadeIn(self.label, shift=RIGHT * 0.1),
            FadeIn(self.boxes),
            *[FadeIn(t) for t in self.texts],
            lag_ratio=0.04,
        )

    def update(self, values: list[int], dim: list[bool] | None = None, flash=theme.ACCENT) -> list[Animation]:
        dim = list(dim) if dim is not None else self.dim
        animations: list[Animation] = []
        for i, value in enumerate(values):
            changed_value = value != self.values[i]
            changed_dim = dim[i] != self.dim[i]
            if not changed_value and not changed_dim:
                continue
            self.values[i] = value
            self.dim[i] = dim[i]
            new = self.make_text(i, value).move_to(self.center(i))
            if changed_value and flash is not None:
                new.set_color(flash)
                self.marked.add(i)
            animations.append(Transform(self.texts[i], new))
        return animations

    def changed(self, values: list[int]) -> list[int]:
        return [i for i, v in enumerate(values) if v != self.values[i]]

    def mark(self, index: int, color) -> list[Animation]:
        i = index - 1
        self.marked.add(i)
        animations = [self.texts[i].animate.set_color(color)]
        if len(self.boxes):
            animations.append(self.boxes[i].animate.set_stroke(color, width=3))
        return animations

    def reset(self, keep: set[int] | None = None) -> list[Animation]:
        kept = {k - 1 for k in (keep or set())} & self.marked
        animations: list[Animation] = []
        for i in sorted(self.marked - kept):
            animations.append(self.texts[i].animate.set_color(self.text_color(i)))
            if len(self.boxes):
                animations.append(self.boxes[i].animate.set_stroke(theme.SECONDARY, width=1.5))
        self.marked = kept
        return animations


class MemoryView:
    def __init__(self, state: dict, n: int, left_x: float, top_y: float):
        self.n = n
        self.slots = max(2 * n - 1, 0)
        step = theme.ROW_STEP
        x_dim = self.dsu_dim(state)
        v_dim = self.tree_dim(state)
        y = top_y
        self.dsu_title = Text("DSU auxiliar  (x = 1 … n)", font_size=theme.GROUP_TITLE_SIZE, color=theme.SECONDARY)
        self.dsu_title.move_to(np.array([left_x, y, 0]), aligned_edge=LEFT)
        y -= step
        self.x_index = ArrayRow("x", list(range(1, n + 1)), left_x, y, is_header=True)
        y -= step
        self.rows: dict[str, ArrayRow] = {}
        self.rows["padre"] = ArrayRow("padre[x]", state["padre"], left_x, y)
        y -= step
        self.rows["tam"] = ArrayRow("tam[x]", state["tam"], left_x, y, dim=x_dim)
        y -= step
        self.rows["nodo"] = ArrayRow("nodo[x]", state["nodo"], left_x, y, dim=x_dim)
        y -= step * 1.35
        self.tree_title = Text(
            "árbol de historia  (v = 1 … 2n − 1)", font_size=theme.GROUP_TITLE_SIZE, color=theme.SECONDARY
        )
        self.tree_title.move_to(np.array([left_x, y, 0]), aligned_edge=LEFT)
        y -= step
        self.v_index = ArrayRow("v", list(range(1, self.slots + 1)), left_x, y, is_header=True)
        y -= step
        self.rows["padreArbol"] = ArrayRow("padreÁrbol[v]", state["padreArbol"], left_x, y, dim=v_dim)
        y -= step
        self.rows["tiempo"] = ArrayRow("t[v]", state["tiempo"], left_x, y, dim=v_dim, color=theme.UNION_STROKE)
        y -= step
        self.rows["hijoIzq"] = ArrayRow("hijoIzq[v]", state["hijoIzq"], left_x, y, dim=v_dim)
        y -= step
        self.rows["hijoDer"] = ArrayRow("hijoDer[v]", state["hijoDer"], left_x, y, dim=v_dim)

    def dsu_dim(self, state: dict) -> list[bool]:
        return [state["padre"][i] != i + 1 for i in range(self.n)]

    def tree_dim(self, state: dict) -> list[bool]:
        return [v > state["nodos"] for v in range(1, self.slots + 1)]

    def dim_for(self, name: str, state: dict) -> list[bool]:
        if name in ("tam", "nodo"):
            return self.dsu_dim(state)
        if name == "padre":
            return [False] * self.n
        return self.tree_dim(state)

    def update(self, names: list[str], state: dict, flash=theme.ACCENT) -> list[Animation]:
        animations: list[Animation] = []
        for name in names:
            animations += self.rows[name].update(state[name], self.dim_for(name, state), flash)
        return animations

    def refresh_dim(self, state: dict) -> list[Animation]:
        animations: list[Animation] = []
        for name, row in self.rows.items():
            animations += row.update(row.values, self.dim_for(name, state), None)
        return animations

    def dsu_group(self) -> list[ArrayRow]:
        return [self.x_index, self.rows["padre"], self.rows["tam"], self.rows["nodo"]]

    def tree_group(self) -> list[ArrayRow]:
        return [self.v_index, self.rows["padreArbol"], self.rows["tiempo"], self.rows["hijoIzq"], self.rows["hijoDer"]]

    def reset(self, keep: dict[str, set[int]] | None = None) -> list[Animation]:
        keep = keep or {}
        animations: list[Animation] = []
        for name, row in self.rows.items():
            animations += row.reset(keep.get(name))
        return animations

    def everything(self) -> VGroup:
        return VGroup(
            self.dsu_title,
            self.tree_title,
            self.x_index.group,
            self.v_index.group,
            *[row.group for row in self.rows.values()],
        )
