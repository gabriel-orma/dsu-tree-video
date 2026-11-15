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
from tree_view import HistoryTreeView


class Narrator:
    def __init__(self, scene: Scene, captions: Captions):
        self.scene = scene
        self.captions = captions

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


class TreePlayer(Narrator):
    def __init__(self, scene: Scene, view: HistoryTreeView, captions: Captions, speed: float = 1.0):
        super().__init__(scene, captions)
        self.view = view
        self.speed = speed

    def rt(self, base: float) -> float:
        return base * self.speed

    def show_leaves(self, caption: str | None = None) -> None:
        leaves = self.view.leaves()
        self.play(
            LaggedStart(*[GrowFromCenter(leaf) for leaf in leaves], lag_ratio=0.12),
            caption=caption,
            run_time=self.rt(1.4),
        )

    def grow(self, event: dict, caption: str | None = None, pre_caption: str | None = None, extra=()) -> None:
        left, right = event["children"]
        new_node = event["newNode"]
        self.play(
            self.view.highlight(left, theme.ACTIVE),
            self.view.highlight(right, theme.ACTIVE),
            caption=pre_caption,
            run_time=self.rt(theme.FAST),
        )
        node = self.view.make_union(new_node)
        ghost = VGroup(self.view.nodes[left][0].copy(), self.view.nodes[right][0].copy())
        edges = [self.view.make_edge(c, new_node) for c in (left, right)]
        self.play(ReplacementTransform(ghost, node), *extra, caption=caption, run_time=self.rt(theme.RUN))
        self.play(*[Create(edge) for edge in edges], *self.view.reset(), run_time=self.rt(theme.FAST))

    def reject(self, event: dict, caption: str | None = None, extra=()) -> None:
        a, b = event["a"], event["b"]
        self.play(
            self.view.highlight(a, theme.QUERY),
            self.view.highlight(b, theme.QUERY),
            self.view.highlight(event["node"], theme.QUERY),
            Circumscribe(self.view.nodes[event["node"]], color=theme.QUERY),
            *extra,
            caption=caption,
            color=theme.QUERY,
            run_time=self.rt(theme.RUN),
        )
        self.scene.wait(self.rt(0.4))
        self.play(*self.view.reset(), run_time=self.rt(theme.FAST))

    def marker(self, text: str, v: int, corner) -> MathTex:
        mark = MathTex(text, font_size=theme.MARKER_SIZE, color=theme.QUERY)
        return mark.move_to(self.view.point(v) + corner * self.view.radius * 1.3)

    def query(self, event: dict, caption: str | None = None, answer_caption: str | None = None) -> None:
        a, b, answer = event["a"], event["b"], event["answer"]
        self.play(
            self.view.highlight(a, theme.QUERY),
            self.view.highlight(b, theme.QUERY),
            caption=caption,
            run_time=self.rt(theme.FAST),
        )
        markers = {"u": self.marker("u", a, UL), "v": self.marker("v", b, UR)}
        extras: list[Animation] = []
        if event["steps"]:
            self.play(FadeIn(markers["u"]), FadeIn(markers["v"]), run_time=self.rt(0.5))
            extras += [FadeOut(markers["u"]), FadeOut(markers["v"])]
        for u, v, moved, nxt in event["steps"]:
            if nxt < 0:
                break
            side = "u" if moved == u else "v"
            corner = UL if side == "u" else UR
            self.play(
                self.view.highlight_edge(moved, theme.QUERY),
                self.view.highlight(nxt, theme.QUERY),
                markers[side].animate.move_to(self.view.point(nxt) + corner * self.view.radius * 1.3),
                run_time=self.rt(0.6),
            )
        if answer < 0:
            label = MathTex(r"-1", font_size=theme.LABEL_SIZE, color=theme.QUERY)
            top_a = self.view.point(event["climbA"][-1])
            top_b = self.view.point(event["climbB"][-1])
            label.move_to((top_a + top_b) / 2 + UP * 0.8)
            self.play(FadeIn(label), caption=answer_caption, color=theme.QUERY, run_time=self.rt(theme.FAST))
        else:
            meet_id = event["meetNode"]
            meet = self.view.nodes[meet_id]
            label = MathTex(f"t = {answer}", font_size=theme.LABEL_SIZE, color=theme.ANSWER)
            label.next_to(meet, DOWN if self.view.is_leaf(meet_id) else RIGHT, buff=0.25)
            self.play(
                self.view.highlight(meet_id, theme.ANSWER),
                Circumscribe(meet, color=theme.ANSWER),
                FadeIn(label, shift=RIGHT * 0.1),
                caption=answer_caption,
                color=theme.ANSWER,
                run_time=self.rt(theme.RUN),
            )
        extras.append(FadeOut(label))
        self.scene.wait(self.rt(theme.LONG_PAUSE))
        self.play(*extras, *self.view.reset(), run_time=self.rt(theme.FAST))

    def run_quiet(self, events: list[dict]) -> None:
        for event in events:
            if event["op"] == "unite":
                if event["merged"]:
                    self.grow(event)
                else:
                    self.reject(event, caption=f"unite({event['a']}, {event['b']}): ya estaban conectados")
            elif event["op"] == "query":
                a, b, answer = event["a"], event["b"], event["answer"]
                self.query(
                    event,
                    caption=f"whenConnected({a}, {b})",
                    answer_caption=f"whenConnected({a}, {b}) = {answer}",
                )
