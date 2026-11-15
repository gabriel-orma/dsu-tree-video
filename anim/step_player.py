from manim import (
    UL,
    UR,
    Animation,
    Create,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    LaggedStart,
    MathTex,
    ReplacementTransform,
    Scene,
    VGroup,
)

import theme
from array_view import MemoryView
from captions import Captions
from player import Narrator
from tree_view import HistoryTreeView


class StepPlayer(Narrator):
    def __init__(
        self,
        scene: Scene,
        view: HistoryTreeView,
        memory: MemoryView,
        captions: Captions,
        full_unions: set[int],
    ):
        super().__init__(scene, captions)
        self.view = view
        self.memory = memory
        self.full_unions = full_unions
        self.narrated_query = False
        self.state: dict | None = None

    def reset_all(self) -> list[Animation]:
        return self.view.reset() + self.memory.reset()

    def row(self, name: str):
        return self.memory.rows[name]

    def run(self, events: list[dict]) -> None:
        self.state = events[0]
        pending: list[dict] = []
        for event in events[1:]:
            op = event["op"]
            if op == "find":
                pending.append(event)
            elif op == "unite":
                self.on_unite(event, pending)
                pending = []
            elif op == "query":
                self.on_query(event)

    def leaves_animation(self) -> Animation:
        leaves = self.view.leaves()
        return LaggedStart(*[GrowFromCenter(leaf) for leaf in leaves], lag_ratio=0.12)

    def animate_finds(self, finds: list[dict]) -> None:
        padre = self.row("padre")
        if finds and all(len(f["path"]) == 1 for f in finds):
            marks = [m for f in finds for m in padre.mark(f["x"], theme.ACCENT)]
            text = " y ".join(f"padre[{f['x']}] = {f['x']}" for f in finds)
            self.play(*marks, caption=f"find: {text}, así que ya son raíces")
            self.state = finds[-1]
            return
        for find in finds:
            x, path, root = find["x"], find["path"], find["root"]
            if len(path) == 1:
                self.play(*padre.mark(x, theme.ACCENT), caption=f"find({x}): padre[{x}] = {x}, ya es raíz")
            else:
                for v in path[:-1]:
                    self.play(*padre.mark(v, theme.ACTIVE), run_time=0.5)
                hops = ",  ".join(f"padre[{v}] = {w}" for v, w in zip(path, path[1:]))
                self.play(*padre.mark(root, theme.ACCENT), caption=f"find({x}): {hops}  →  raíz {root}")
            if find["compressed"]:
                pairs = ",  ".join(f"padre[{c}] = {r}" for c, r in find["compressed"])
                self.play(
                    *self.memory.update(["padre"], find),
                    caption=f"compresión de caminos: {pairs}\n(la próxima vez se llega directo a la raíz)",
                    color=theme.ACCENT,
                )
            self.state = find

    def on_unite(self, event: dict, finds: list[dict]) -> None:
        a, b = event["a"], event["b"]
        full = not event["merged"] or event["t"] in self.full_unions
        self.play(
            self.view.highlight(a, theme.ACTIVE),
            self.view.highlight(b, theme.ACTIVE),
            caption=f"unite({a}, {b}): primero buscamos la raíz de {a} y la de {b}" if full else None,
            run_time=theme.FAST,
        )
        if full:
            self.animate_finds(finds)
        elif finds:
            self.state = finds[-1]
        if not event["merged"]:
            self.reject(event)
        elif full:
            self.merge_full(event)
        else:
            self.merge_compact(event)
        self.state = event

    def grow_node(self, event: dict, caption: str, *extra: Animation) -> list:
        left, right = event["children"]
        new_node = event["newNode"]
        node = self.view.make_union(new_node)
        ghost = VGroup(self.view.nodes[left][0].copy(), self.view.nodes[right][0].copy())
        edges = [self.view.make_edge(c, new_node) for c in (left, right)]
        self.play(ReplacementTransform(ghost, node), *extra, caption=caption)
        return edges

    def merge_full(self, event: dict) -> None:
        root_a, root_b = event["rootA"], event["rootB"]
        child, parent = event["dsuChild"], event["dsuParent"]
        left, right = event["children"]
        v, t = event["newNode"], event["t"]
        size_a = self.state["tam"][root_a - 1]
        size_b = self.state["tam"][root_b - 1]
        nodo = self.row("nodo")
        self.play(
            *self.view.reset(keep=(left, right)),
            self.view.highlight(left, theme.ACTIVE),
            self.view.highlight(right, theme.ACTIVE),
            *nodo.mark(root_a, theme.ACTIVE),
            *nodo.mark(root_b, theme.ACTIVE),
            caption=f"raíces distintas ({root_a} ≠ {root_b}). En el árbol, sus grupos son\nnodo[{root_a}] = {left}  y  nodo[{root_b}] = {right}",
        )
        tag = self.view.make_tag(v)
        edges = self.grow_node(
            event,
            f"nace el nodo #{v} = n + t encima de ambos, con t[{v}] = {t} e hijos {left} y {right};\n" + f"padreÁrbol[{left}] = padreÁrbol[{right}] = {v}",
            FadeIn(tag),
            *self.memory.update(["padreArbol", "tiempo", "hijoIzq", "hijoDer"], event),
        )
        self.play(*[Create(edge) for edge in edges], run_time=theme.FAST)
        self.play(
            *self.memory.update(["padre", "tam", "nodo"], event),
            caption=f"unión por tamaño (tam {size_a} y {size_b}): padre[{child}] = {parent}, tam[{parent}] = {event['size']};\nnodo[{parent}] = {v}: ahora el nodo #{v} representa a toda la componente",
        )
        self.play(*self.reset_all(), run_time=theme.FAST)

    def merge_compact(self, event: dict) -> None:
        child, parent = event["dsuChild"], event["dsuParent"]
        left, right = event["children"]
        v, t = event["newNode"], event["t"]
        size_a = self.state["tam"][event["rootA"] - 1]
        size_b = self.state["tam"][event["rootB"] - 1]
        edges = self.grow_node(
            event,
            f"unite({event['a']}, {event['b']}): raíces {event['rootA']} y {event['rootB']} → nace el nodo #{v} con t = {t}",
            *self.memory.update(["padreArbol", "tiempo", "hijoIzq", "hijoDer"], event),
        )
        tag = self.view.make_tag(v)
        self.play(
            *[Create(edge) for edge in edges],
            FadeIn(tag),
            *self.memory.update(["padre", "tam", "nodo"], event),
            caption=f"tam {size_a} y {size_b}: padre[{child}] = {parent},  tam[{parent}] = {event['size']},  nodo[{parent}] = {v}",
        )
        self.play(*self.reset_all(), run_time=theme.FAST)

    def reject(self, event: dict) -> None:
        node = event["node"]
        self.play(
            *self.view.reset(keep=(event["a"], event["b"], node)),
            self.view.highlight(event["a"], theme.QUERY),
            self.view.highlight(event["b"], theme.QUERY),
            self.view.highlight(node, theme.QUERY),
            caption=f"misma raíz ({event['rootA']} = {event['rootB']}): ya estaban conectados.\nunite devuelve false: no nace ningún nodo y t no avanza",
            color=theme.QUERY,
        )
        self.play(*self.reset_all(), run_time=theme.FAST)

    def marker(self, text: str, v: int, corner) -> MathTex:
        mark = MathTex(text, font_size=theme.MARKER_SIZE, color=theme.QUERY)
        return mark.move_to(self.view.point(v) + corner * self.view.radius * 1.35)

    def on_query(self, event: dict) -> None:
        a, b, answer = event["a"], event["b"], event["answer"]
        narrate = not self.narrated_query and bool(event["steps"])
        tiempo, padre_arbol = self.row("tiempo"), self.row("padreArbol")
        self.play(
            self.view.highlight(a, theme.QUERY),
            self.view.highlight(b, theme.QUERY),
            caption=f"whenConnected({a}, {b}): ¿en qué momento se conectaron?",
        )
        markers = {"u": self.marker("u", a, UL), "v": self.marker("v", b, UR)}
        extras: list[Animation] = []
        if event["steps"]:
            self.play(
                FadeIn(markers["u"]),
                FadeIn(markers["v"]),
                caption=(
                    f"u = {a}, v = {b}. En cada paso leemos t[u] y t[v]\ny el de t menor sube por padreÁrbol"
                    if narrate
                    else None
                ),
                run_time=theme.FAST,
            )
            extras += [FadeOut(markers["u"]), FadeOut(markers["v"])]
        if narrate:
            self.narrated_query = True

        for u, v, moved, nxt in event["steps"]:
            side = "u" if moved == u else "v"
            tu, tv = tiempo.values[u - 1], tiempo.values[v - 1]
            relation = "<" if tu < tv else ("=" if tu == tv else ">")
            marks = self.memory.reset({"tiempo": {u, v}, "padreArbol": {moved}})
            marks += tiempo.mark(u, theme.ACTIVE) + tiempo.mark(v, theme.ACTIVE)
            marks += padre_arbol.mark(moved, theme.QUERY)
            if nxt < 0:
                self.play(
                    *marks,
                    caption=f"t[{u}] = {tu} {relation} t[{v}] = {tv}, pero padreÁrbol[{moved}] = −1:\n{side} ya es raíz y no hay ancestro común",
                    color=theme.QUERY,
                )
                break
            corner = UL if side == "u" else UR
            tie = " (empate: sube u)" if tu == tv else ""
            self.play(
                *marks,
                self.view.highlight_edge(moved, theme.QUERY),
                self.view.highlight(nxt, theme.QUERY),
                markers[side].animate.move_to(self.view.point(nxt) + corner * self.view.radius * 1.35),
                caption=(
                    f"t[{u}] = {tu} {relation} t[{v}] = {tv}{tie}:  sube {side},  padreÁrbol[{moved}] = {nxt}"
                    if narrate
                    else None
                ),
                run_time=theme.RUN if narrate else 0.7,
            )

        if answer < 0:
            self.play(
                caption=f"whenConnected({a}, {b}) = −1: nunca se conectaron",
                color=theme.QUERY,
            )
        else:
            meet = event["meetNode"]
            reached = f"u = v = #{meet}: " if event["steps"] else f"u = v desde el inicio: "
            self.play(
                *self.memory.reset({"tiempo": {meet}}),
                self.view.highlight(meet, theme.ANSWER),
                *tiempo.mark(meet, theme.ANSWER),
                caption=f"{reached}whenConnected({a}, {b}) = t[{meet}] = {answer}",
                color=theme.ANSWER,
            )
        self.scene.wait(theme.LONG_PAUSE)
        self.play(*extras, *self.reset_all(), run_time=theme.FAST)
