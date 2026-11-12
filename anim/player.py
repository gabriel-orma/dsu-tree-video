from manim import (
    DOWN,
    RIGHT,
    UP,
    Animation,
    Circumscribe,
    Create,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    Indicate,
    LaggedStart,
    MathTex,
    ReplacementTransform,
    Scene,
    VGroup,
)

import theme
from captions import Captions
from tree_view import HistoryTreeView


class TracePlayer:
    def __init__(self, scene: Scene, view: HistoryTreeView, captions: Captions):
        self.scene = scene
        self.view = view
        self.captions = captions

    def play(self, *animations: Animation, caption: str | None = None, caption_color=None, run_time=theme.RUN):
        batch = list(animations)
        if caption is not None:
            batch += self.captions.show(caption, caption_color)
        if batch:
            self.scene.play(*batch, run_time=run_time)

    def run(self, events: list[dict], skip: set[str] = frozenset({"find"})) -> None:
        for event in events:
            if event["op"] in skip:
                continue
            getattr(self, f"on_{event['op']}")(event)

    def on_init(self, event: dict) -> None:
        leaves = self.view.leaves()
        n = event["n"]
        self.play(
            LaggedStart(*[GrowFromCenter(leaf) for leaf in leaves], lag_ratio=0.15),
            caption=f"{n} elementos, cada uno en su propia componente",
            run_time=1.4,
        )
        self.scene.wait(theme.PAUSE)

    def on_unite(self, event: dict) -> None:
        a, b = event["a"], event["b"]
        if not event["merged"]:
            self.on_unite_rejected(event)
            return
        left, right = event["children"]
        new_node = event["newNode"]
        self.play(
            self.view.highlight(left, theme.ACTIVE),
            self.view.highlight(right, theme.ACTIVE),
            caption=f"unite({a}, {b})",
            run_time=theme.FAST,
        )
        node = self.view.make_union(new_node)
        ghost = VGroup(self.view.nodes[left][0].copy(), self.view.nodes[right][0].copy())
        self.play(
            ReplacementTransform(ghost, node),
            caption=f"unite({a}, {b}): nace el nodo de unión con t = {event['t']}",
        )
        edges = [self.view.make_edge(child, new_node) for child in (left, right)]
        self.play(*[Create(edge) for edge in edges], *self.view.reset(), run_time=theme.FAST)
        self.scene.wait(theme.PAUSE)

    def on_unite_rejected(self, event: dict) -> None:
        a, b = event["a"], event["b"]
        self.play(
            self.view.highlight(a, theme.QUERY),
            self.view.highlight(b, theme.QUERY),
            caption=f"unite({a}, {b}): ya estaban conectados\nno se crea ningún nodo",
            caption_color=theme.QUERY,
        )
        self.play(Indicate(self.view.nodes[event["node"]], color=theme.QUERY, scale_factor=1.15))
        self.scene.wait(theme.PAUSE)
        self.play(*self.view.reset(), run_time=theme.FAST)

    def on_query(self, event: dict) -> None:
        a, b, answer = event["a"], event["b"], event["answer"]
        self.play(
            self.view.highlight(a, theme.QUERY),
            self.view.highlight(b, theme.QUERY),
            caption=f"¿Cuándo se conectaron {a} y {b}?",
        )
        for climb in (event["climbA"], event["climbB"]):
            for child, parent in zip(climb, climb[1:]):
                self.play(
                    self.view.highlight_edge(child, theme.QUERY),
                    self.view.highlight(parent, theme.QUERY),
                    run_time=theme.FAST,
                )

        extras: list[Animation] = []
        if answer < 0:
            top_a = self.view.point(event["climbA"][-1])
            top_b = self.view.point(event["climbB"][-1])
            label = MathTex(r"t = -1", font_size=theme.LABEL_SIZE, color=theme.QUERY)
            label.move_to((top_a + top_b) / 2 + UP * 0.9)
            self.play(
                FadeIn(label, shift=UP * 0.1),
                caption=f"whenConnected({a}, {b}) = −1\nnunca se conectaron",
                caption_color=theme.QUERY,
            )
            extras.append(FadeOut(label))
        else:
            meet = self.view.nodes[event["meetNode"]]
            label = MathTex(f"t = {answer}", font_size=theme.LABEL_SIZE, color=theme.ANSWER)
            side = DOWN if event["meetNode"] <= self.view.layout.n else RIGHT
            label.next_to(meet, side, buff=0.25)
            self.play(
                self.view.highlight(event["meetNode"], theme.ANSWER),
                Circumscribe(meet, color=theme.ANSWER),
                FadeIn(label, shift=RIGHT * 0.1),
                caption=f"whenConnected({a}, {b}) = {answer}",
                caption_color=theme.ANSWER,
            )
            extras.append(FadeOut(label))
        self.scene.wait(theme.LONG_PAUSE)
        self.play(*extras, *self.view.reset(), run_time=theme.FAST)

    def on_connected(self, event: dict) -> None:
        a, b, answer = event["a"], event["b"], event["answer"]
        color = theme.ANSWER if answer else theme.QUERY
        self.play(
            Indicate(self.view.nodes[a], color=color),
            Indicate(self.view.nodes[b], color=color),
            caption=f"connected({a}, {b}) = {'sí' if answer else 'no'}",
            caption_color=color,
        )
        self.scene.wait(theme.PAUSE)
