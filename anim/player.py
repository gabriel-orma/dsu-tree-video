from manim import (
    DOWN,
    RIGHT,
    UL,
    UP,
    UR,
    Animation,
    Circumscribe,
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
from captions import Captions
from dsu_panel import DsuPanel
from tree_view import HistoryTreeView


class TracePlayer:
    def __init__(
        self,
        scene: Scene,
        view: HistoryTreeView,
        captions: Captions,
        panel: DsuPanel | None = None,
        detail: bool = True,
    ):
        self.scene = scene
        self.view = view
        self.captions = captions
        self.panel = panel
        self.detail = detail and panel is not None
        self.explained_query = False
        self.explained_unite = False
        self.quiet_unites = False

    def hold(self, text: str | None, elapsed: float = 0.0) -> None:
        if text is None:
            return
        if self.captions.enabled:
            words = len(text.split())
            needed = max(theme.READ_MIN, words * theme.READ_SECONDS_PER_WORD)
            self.scene.wait(max(theme.MIN_HOLD, needed - elapsed))
        else:
            self.scene.wait(theme.PAUSE / 2)

    def play(self, *animations: Animation, caption: str | None = None, color=None, run_time=theme.RUN):
        batch = list(animations)
        if caption is not None:
            batch += self.captions.show(caption, color)
        if batch:
            self.scene.play(*batch, run_time=run_time)
        self.hold(caption, run_time if batch else 0.0)

    def say(self, caption: str, color=None) -> None:
        self.play(caption=caption, color=color)

    def panel_anims(self, method: str, *args, **kwargs) -> list[Animation]:
        if self.panel is None:
            return []
        result = getattr(self.panel, method)(*args, **kwargs)
        return result if isinstance(result, list) else [result]

    def reset_all(self) -> list[Animation]:
        return self.view.reset() + self.panel_anims("reset")

    def run(self, events: list[dict]) -> None:
        pending_finds: list[dict] = []
        for event in events:
            op = event["op"]
            if op == "find":
                pending_finds.append(event)
                continue
            if op in ("unite", "connected"):
                getattr(self, f"on_{op}")(event, pending_finds)
                pending_finds = []
            else:
                getattr(self, f"on_{op}")(event)

    def on_init(self, event: dict) -> None:
        leaves = self.view.leaves()
        extra = [self.panel.appear()] if self.panel is not None else []
        self.play(
            LaggedStart(*[GrowFromCenter(leaf) for leaf in leaves], lag_ratio=0.15),
            *extra,
            caption=None if self.quiet_unites else f"{event['n']} elementos, cada uno en su propia componente",
            run_time=1.6,
        )
        if self.panel is not None:
            self.say("DSU auxiliar: padre[x] lleva hasta la raíz;\nnodo[raíz] es el nodo de esa componente en el árbol de historia")

    def animate_finds(self, finds: list[dict]) -> None:
        trivial = [f for f in finds if len(f["path"]) == 1]
        if len(trivial) == len(finds) and finds:
            marks = [m for f in finds for m in self.panel.mark(f["x"], theme.ACCENT)]
            names = " y ".join(f"find({f['x']}) = {f['x']}" for f in finds)
            self.play(*marks, caption=f"{names}: padre[x] = x, ya son raíces")
            return
        for find in finds:
            self.animate_find(find)

    def animate_find(self, event: dict) -> None:
        x, path, root = event["x"], event["path"], event["root"]
        if len(path) == 1:
            self.play(*self.panel.mark(x, theme.ACCENT), caption=f"find({x}) = {x}: ya es raíz")
        else:
            for v in path[:-1]:
                self.play(*self.panel.mark(v, theme.ACTIVE), run_time=theme.FAST * 0.7)
            self.play(
                *self.panel.mark(root, theme.ACCENT),
                caption=f"find({x}): " + " → ".join(map(str, path)) + f", la raíz es {root}",
            )
        for child, new_parent in event["compressed"]:
            self.play(
                self.panel.set_parent(child, new_parent),
                caption=f"compresión de caminos: padre[{child}] ← {new_parent}\n(la próxima vez, {child} llega directo a la raíz)",
                color=theme.ACCENT,
            )

    def wants_detail(self, event: dict, finds: list[dict]) -> bool:
        if not self.detail:
            return False
        interesting = (
            not self.explained_unite
            or not event["merged"]
            or any(len(f["path"]) > 1 or f["compressed"] for f in finds)
        )
        self.explained_unite = True
        return interesting

    def on_unite(self, event: dict, finds: list[dict]) -> None:
        a, b = event["a"], event["b"]
        full = self.wants_detail(event, finds)
        if full:
            self.play(
                self.view.highlight(a, theme.ACTIVE),
                self.view.highlight(b, theme.ACTIVE),
                caption=f"unite({a}, {b}): buscamos la raíz de {a} y la de {b}",
                run_time=theme.FAST,
            )
            self.animate_finds(finds)
        if not event["merged"]:
            self.reject(event)
        elif full:
            self.merge_full(event)
        elif self.panel is not None:
            self.merge_brief(event)
        else:
            self.merge_minimal(event)

    def grow_node(self, event: dict, caption: str | None, *extra: Animation) -> None:
        left, right = event["children"]
        new_node = event["newNode"]
        node = self.view.make_union(new_node)
        ghost = VGroup(self.view.nodes[left][0].copy(), self.view.nodes[right][0].copy())
        self.play(ReplacementTransform(ghost, node), *extra, caption=caption)
        edges = [self.view.make_edge(c, new_node) for c in (left, right)]
        self.play(*[Create(edge) for edge in edges], *self.reset_all(), run_time=theme.FAST)

    def merge_full(self, event: dict) -> None:
        root_a, root_b = event["rootA"], event["rootB"]
        child, parent = event["dsuChild"], event["dsuParent"]
        left, right = event["children"]
        t = event["t"]
        self.play(
            self.panel.set_parent(child, parent),
            caption=f"raíces distintas ({root_a} ≠ {root_b}): se unen.\nunión por tamaño: la raíz {child} cuelga de {parent}",
        )
        self.play(
            *self.view.reset(keep=(left, right)),
            self.view.highlight(left, theme.ACTIVE),
            self.view.highlight(right, theme.ACTIVE),
            *self.panel.mark(root_a, theme.ACTIVE, cols=(2,)),
            *self.panel.mark(root_b, theme.ACTIVE, cols=(2,)),
            caption=f"en el árbol: nodo[{root_a}] = {self.view.short(left)}  y  nodo[{root_b}] = {self.view.short(right)}",
        )
        self.grow_node(
            event,
            f"nace el nodo t = {t}, padre de ambos: «se unieron en el momento {t}»\nahora nodo[{parent}] = (t={t})",
            self.panel.set_node(parent, event["newNode"]),
            self.panel.set_node(child, None),
        )

    def merge_brief(self, event: dict) -> None:
        child, parent = event["dsuChild"], event["dsuParent"]
        left, right = event["children"]
        t = event["t"]
        self.play(
            self.view.highlight(left, theme.ACTIVE),
            self.view.highlight(right, theme.ACTIVE),
            self.panel.set_parent(child, parent),
            caption=f"unite({event['a']}, {event['b']}): raíces {event['rootA']} y {event['rootB']}; {child} cuelga de {parent}",
        )
        self.grow_node(
            event,
            f"nace el nodo t = {t};  nodo[{parent}] = (t={t})",
            self.panel.set_node(parent, event["newNode"]),
            self.panel.set_node(child, None),
        )

    def merge_minimal(self, event: dict) -> None:
        left, right = event["children"]
        self.play(
            self.view.highlight(left, theme.ACTIVE),
            self.view.highlight(right, theme.ACTIVE),
            caption=None if self.quiet_unites else f"unite({event['a']}, {event['b']}): nace el nodo t = {event['t']}",
            run_time=theme.FAST * 0.6 if self.quiet_unites else theme.FAST,
        )
        self.grow_node(event, None)

    def reject(self, event: dict) -> None:
        a, b = event["a"], event["b"]
        self.play(
            *self.view.reset(keep=(a, b)),
            self.view.highlight(a, theme.QUERY),
            self.view.highlight(b, theme.QUERY),
            self.view.highlight(event["node"], theme.QUERY),
            Circumscribe(self.view.nodes[event["node"]], color=theme.QUERY),
            caption=f"misma raíz ({event['rootA']} = {event['rootB']}): ya estaban conectados.\nunite devuelve false: no nace ningún nodo y t no avanza",
            color=theme.QUERY,
        )
        self.play(*self.reset_all(), run_time=theme.FAST)

    def on_connected(self, event: dict, finds: list[dict]) -> None:
        a, b, answer = event["a"], event["b"], event["answer"]
        self.play(
            self.view.highlight(a, theme.ACTIVE),
            self.view.highlight(b, theme.ACTIVE),
            caption=f"connected({a}, {b}): ¿misma componente hoy?",
        )
        if self.detail:
            self.animate_finds(finds)
        color = theme.ANSWER if answer else theme.QUERY
        verdict = "sí" if answer else "no"
        self.play(
            self.view.highlight(a, color),
            self.view.highlight(b, color),
            caption=f"raíces {event['rootA']} y {event['rootB']}:  connected({a}, {b}) = {verdict}",
            color=color,
        )
        self.play(*self.reset_all(), run_time=theme.FAST)

    def marker(self, text: str, v: int, corner) -> MathTex:
        mark = MathTex(text, font_size=theme.MARKER_SIZE, color=theme.QUERY)
        return mark.move_to(self.view.point(v) + corner * theme.NODE_RADIUS * 1.25)

    def on_query(self, event: dict) -> None:
        a, b, answer = event["a"], event["b"], event["answer"]
        self.play(
            self.view.highlight(a, theme.QUERY),
            self.view.highlight(b, theme.QUERY),
            caption=f"whenConnected({a}, {b}): ¿cuándo se conectaron {a} y {b}?",
        )
        narrate = not self.explained_query and bool(event["steps"])
        markers = {"u": self.marker("u", a, UL), "v": self.marker("v", b, UR)}
        extras: list[Animation] = []
        if event["steps"]:
            if narrate:
                self.explained_query = True
            self.play(
                FadeIn(markers["u"]),
                FadeIn(markers["v"]),
                caption=(
                    f"u parte de {a} y v de {b}. Como t crece hacia arriba,\nsube siempre el que tenga t menor hasta encontrarse"
                    if narrate
                    else None
                ),
                run_time=theme.FAST,
            )
            extras += [FadeOut(markers["u"]), FadeOut(markers["v"])]
        else:
            self.say(f"{a} consigo mismo: no hay que subir")

        for u, v, moved, nxt in event["steps"]:
            side = "u" if moved == u else "v"
            tu, tv = self.view.time(u), self.view.time(v)
            if nxt < 0:
                self.say(f"{self.view.short(moved)} es raíz: {side} ya no puede subir", color=theme.QUERY)
                break
            relation = "<" if tu < tv else ("=" if tu == tv else ">")
            reason = "empate: sube u" if tu == tv else f"sube {side}"
            corner = UL if side == "u" else UR
            self.play(
                self.view.highlight_edge(moved, theme.QUERY),
                self.view.highlight(nxt, theme.QUERY),
                markers[side].animate.move_to(self.view.point(nxt) + corner * theme.NODE_RADIUS * 1.25),
                caption=f"t(u) = {tu} {relation} t(v) = {tv}:  {reason}" if narrate else None,
                run_time=theme.RUN if narrate else theme.FAST,
            )

        if answer < 0:
            top_a = self.view.point(event["climbA"][-1])
            top_b = self.view.point(event["climbB"][-1])
            label = MathTex(r"t = -1", font_size=theme.LABEL_SIZE, color=theme.QUERY)
            label.move_to((top_a + top_b) / 2 + UP * 0.9)
            self.play(
                FadeIn(label, shift=UP * 0.1),
                caption=f"sin ancestro común: whenConnected({a}, {b}) = −1, nunca se conectaron",
                color=theme.QUERY,
            )
            extras.append(FadeOut(label))
        else:
            meet_id = event["meetNode"]
            meet = self.view.nodes[meet_id]
            label = MathTex(f"t = {answer}", font_size=theme.LABEL_SIZE, color=theme.ANSWER)
            side = DOWN if self.view.is_leaf(meet_id) else RIGHT
            label.next_to(meet, side, buff=0.3)
            reached = f"se encuentran en {self.view.short(meet_id)}:  " if event["steps"] else ""
            self.play(
                self.view.highlight(meet_id, theme.ANSWER),
                Circumscribe(meet, color=theme.ANSWER),
                FadeIn(label, shift=RIGHT * 0.1),
                caption=f"{reached}whenConnected({a}, {b}) = {answer}",
                color=theme.ANSWER,
            )
            extras.append(FadeOut(label))
        self.scene.wait(theme.LONG_PAUSE)
        self.play(*extras, *self.reset_all(), run_time=theme.FAST)
