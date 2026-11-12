from manim import (
    DL,
    DOWN,
    DR,
    LEFT,
    RIGHT,
    UP,
    Arrow,
    Circle,
    FadeIn,
    FadeOut,
    LaggedStart,
    MathTex,
    ReplacementTransform,
    RoundedRectangle,
    Scene,
    Text,
    VGroup,
    Write,
    np,
)

import theme
from captions import Captions
from dsu_panel import DsuPanel
from player import TracePlayer
from slides import bullet_lines, heading, reading_time, show_slide
from trace_loader import PROJECT_ROOT, load_trace, trace_dir
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
        entry(theme.LEAF_STROKE, theme.LEAF_FILL, theme.LEAF_FILL_OPACITY, "elemento (hoja)"),
        entry(theme.UNION_STROKE, theme.BACKGROUND, 1, "nodo de unión (momento t)"),
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
    return items.to_corner(DR, buff=0.35)


class TraceScene(Scene):
    SCENARIO = "demo"
    WITH_PANEL = True
    DETAIL = True

    def setup(self):
        self.camera.background_color = theme.BACKGROUND
        self.events = load_trace(self.SCENARIO)
        layout = history_layout(self.events)
        self.view = HistoryTreeView(layout)
        panel = None
        if self.WITH_PANEL:
            panel = DsuPanel(self.events[0], layout, np.array([*theme.PANEL_CENTER, 0.0]))
        self.captions = Captions()
        self.player = TracePlayer(self, self.view, self.captions, panel, self.DETAIL)
        self.add(source_footer(), legend())

    def finish(self):
        self.player.play(*self.captions.clear(), *self.player.reset_all())
        self.wait(1)


class Titulo(Scene):
    def construct(self):
        self.camera.background_color = theme.BACKGROUND
        hook = Text("¿En qué momento se conectaron estos dos elementos?", font_size=40)
        self.play(Write(hook), run_time=2)
        self.wait(reading_time(hook.text))
        title = Text("DSU Tree", font_size=theme.TITLE_SIZE)
        subtitle = Text("el DSU con memoria", font_size=40, color=theme.DETAIL)
        course = Text(
            "Proyecto Final 2 · CS2023 Algoritmos y Estructuras de Datos · UTEC 2026-2",
            font_size=24,
            color=theme.SECONDARY,
        )
        block = VGroup(title, subtitle, course).arrange(DOWN, buff=0.4)
        self.play(ReplacementTransform(hook, title), run_time=1.4)
        self.play(FadeIn(subtitle, shift=UP * 0.2), FadeIn(course, shift=UP * 0.2), run_time=1.2)
        self.wait(2.5)
        self.play(FadeOut(block), run_time=theme.FAST)


class Concepto(Scene):
    def construct(self):
        self.camera.background_color = theme.BACKGROUND

        lines = [
            ("find(x): la raíz (representante) de la componente de x.", theme.TEXT_COLOR),
            ("unite(a, b): fusiona las componentes de a y de b.", theme.TEXT_COLOR),
            ("Sabe si a y b están conectados… pero olvida cuándo pasó.", theme.ACCENT),
        ]
        show_slide(self, heading("Recordatorio: DSU (Union-Find)"), bullet_lines(lines), [t for t, _ in lines])

        intro = Text(
            "Un DSU Tree guarda la historia de las uniones en un árbol.",
            font_size=theme.BODY_SIZE,
            color=theme.DETAIL,
        )
        ops = [
            ("DSUTree(n)", "n elementos, cada uno en su propia componente"),
            ("unite(a, b)", "une sus componentes y registra el momento t"),
            ("connected(a, b)", "¿están hoy en la misma componente?"),
            ("whenConnected(a, b)", "momento t en que se conectaron (−1 si nunca)"),
        ]
        rows = VGroup()
        for signature, meaning in ops:
            sig = Text(signature, font=theme.MONO_FONT, font_size=28, color=theme.UNION_STROKE)
            text = Text(meaning, font_size=28)
            rows.add(VGroup(sig, text))
        for row in rows:
            row[1].next_to(row[0], RIGHT, buff=0)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        sig_width = max(row[0].width for row in rows)
        for row in rows:
            row[1].next_to(row[0], RIGHT, buff=0).align_to(rows[0][0], LEFT).shift(RIGHT * (sig_width + 0.5))
        box = RoundedRectangle(width=rows.width + 0.8, height=rows.height + 0.7, corner_radius=0.15)
        box.set_stroke(theme.SECONDARY, width=1.5)
        tda_label = Text("TDA: conectividad incremental con historia", font_size=26, color=theme.SECONDARY)
        tda = VGroup(box, rows)
        rows.move_to(box)
        body = VGroup(intro, VGroup(tda_label, tda).arrange(DOWN, buff=0.2)).arrange(DOWN, buff=0.5)
        show_slide(
            self,
            heading("DSU Tree: el DSU con memoria"),
            body,
            [intro.text, "TDA conectividad incremental con historia"] + [f"{s} {m}" for s, m in ops],
        )

        uses = [
            ("Redes que se conectan con el tiempo: ¿desde cuándo hay conexión?", theme.TEXT_COLOR),
            ("Árbol de reconstrucción de Kruskal: arista más pesada entre a y b en el MST.", theme.TEXT_COLOR),
            ("Consultas offline de conectividad sobre una secuencia de uniones.", theme.TEXT_COLOR),
        ]
        show_slide(self, heading("¿Para qué se usa?"), bullet_lines(uses), [t for t, _ in uses])

        variant = [
            ("Hojas 1 … n: los elementos originales.", theme.LEAF_STROKE),
            ("Cada unión efectiva crea un nodo n + t, padre de ambas componentes, que guarda t.", theme.UNION_STROKE),
            ("t crece hacia arriba ⇒ whenConnected(a, b) = t del ancestro común más cercano.", theme.ANSWER),
        ]
        show_slide(
            self,
            heading("Variante implementada: un nodo nuevo por unión"),
            bullet_lines(variant),
            [t for t, _ in variant],
        )


def excerpt(lines: list[str], width: int = 34) -> VGroup:
    shown = [line if len(line) <= width else line[: width - 1] + "…" for line in lines]
    group = VGroup(*[Text(line, font=theme.MONO_FONT, font_size=16, color=theme.DETAIL) for line in shown])
    return group.arrange(DOWN, aligned_edge=LEFT, buff=0.12)


class Tuberia(Scene):
    def construct(self):
        self.camera.background_color = theme.BACKGROUND
        title = heading("¿De dónde sale la animación?")
        stages = [
            ("scenarios/demo.txt", "operaciones"),
            ("dsu_tree.cpp", "lógica real, C++17"),
            ("demo.json", "traza de eventos"),
            ("Manim", "solo dibuja la traza"),
        ]
        boxes = VGroup()
        for name, role in stages:
            label = VGroup(
                Text(name, font=theme.MONO_FONT, font_size=22, color=theme.UNION_STROKE),
                Text(role, font_size=20, color=theme.TEXT_COLOR),
            ).arrange(DOWN, buff=0.15)
            if label.width > 2.6:
                label.scale_to_fit_width(2.6)
            frame = RoundedRectangle(width=2.95, height=1.2, corner_radius=0.15).set_stroke(theme.SECONDARY, width=1.5)
            boxes.add(VGroup(frame, label.move_to(frame)))
        boxes.arrange(RIGHT, buff=0.45).shift(UP * 0.8)
        arrows = VGroup(*[
            Arrow(boxes[i].get_right(), boxes[i + 1].get_left(), buff=0.08, stroke_width=3, color=theme.SECONDARY)
            for i in range(len(boxes) - 1)
        ])

        scenario_lines = [
            line.strip()
            for line in (PROJECT_ROOT / "scenarios" / "demo.txt").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ][:4]
        trace_lines = [
            line.strip().rstrip(",")
            for line in (trace_dir() / "demo.json").read_text(encoding="utf-8").splitlines()
            if line.strip() not in ("[", "]")
        ][:4]
        left = excerpt(scenario_lines + ["…"]).next_to(boxes[0], DOWN, buff=0.4)
        right = excerpt(trace_lines + ["…"], width=40).next_to(boxes[2], DOWN, buff=0.4)
        right.align_to(boxes[2], LEFT).shift(LEFT * 0.6)

        note = Text(
            "Las trazas se regeneran en cada render: lo que ves es lo que el código realmente hizo.",
            font_size=26,
            color=theme.ACCENT,
        ).to_edge(DOWN, buff=0.7)

        self.play(Write(title), run_time=theme.RUN)
        self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.15) for b in boxes], lag_ratio=0.3), run_time=2)
        self.play(LaggedStart(*[FadeIn(a) for a in arrows], lag_ratio=0.3), run_time=1.2)
        self.play(FadeIn(left, shift=UP * 0.1), FadeIn(right, shift=UP * 0.1), run_time=1.2)
        self.wait(3)
        self.play(FadeIn(note, shift=UP * 0.1), run_time=theme.RUN)
        self.wait(reading_time(note.text) + 1)
        self.play(*[FadeOut(m) for m in (title, boxes, arrows, left, right, note)], run_time=theme.FAST)


class Demo(TraceScene):
    SCENARIO = "demo"

    def construct(self):
        self.player.run(self.events)
        self.finish()


class PeorCaso(TraceScene):
    SCENARIO = "cadena"
    WITH_PANEL = False
    DETAIL = False

    def construct(self):
        self.player.explained_query = True
        self.player.quiet_unites = True
        self.player.say("peor caso: una cadena de uniones, cada una con la componente que crece", color=theme.QUERY)
        self.player.run(self.events)
        self.player.say(
            "la altura del árbol de historia llega a n − 1:\nuna consulta puede recorrer O(n) nodos",
            color=theme.QUERY,
        )
        self.finish()


class Complejidad(Scene):
    def construct(self):
        self.camera.background_color = theme.BACKGROUND
        title = heading("Complejidad")
        rows_data = [
            ("unite(a, b)", r"O(\alpha(n))\ \text{amortizado}", "dos find + O(1) para crear el nodo nuevo"),
            ("connected(a, b)", r"O(\alpha(n))\ \text{amortizado}", "dos find en el DSU auxiliar"),
            ("whenConnected(a, b)", r"O(h) \le O(n)", "sube por el árbol de historia; h es su altura"),
            ("memoria", r"O(n)", "a lo más 2n − 1 nodos en el árbol de historia"),
        ]
        rows = VGroup()
        for op, cost, why in rows_data:
            rows.add(VGroup(
                Text(op, font=theme.MONO_FONT, font_size=24, color=theme.UNION_STROKE),
                MathTex(cost, font_size=34, color=theme.ANSWER),
                Text(why, font_size=22, color=theme.TEXT_COLOR),
            ))
        col_x = [-6.4, -2.6, 1.0]
        for i, row in enumerate(rows):
            y = 1.6 - i * 0.95
            if row[2].width > 5.6:
                row[2].scale_to_fit_width(5.6)
            for col, mob in enumerate(row):
                mob.move_to(np.array([col_x[col], y, 0]), aligned_edge=LEFT)
        notes = VGroup(
            MathTex(r"\alpha(n) \le 4 \text{ para cualquier } n \text{ práctico}", font_size=30, color=theme.DETAIL),
            Text("Mejora posible: saltos binarios (binary lifting) → O(log n) por consulta.", font_size=24, color=theme.SECONDARY),
        ).arrange(DOWN, buff=0.3).to_edge(DOWN, buff=0.9)

        self.play(Write(title), run_time=theme.RUN)
        for row in rows:
            self.play(LaggedStart(*[FadeIn(m, shift=RIGHT * 0.1) for m in row], lag_ratio=0.25), run_time=1.2)
            self.wait(reading_time(row[0].text, row[2].text))
        self.play(FadeIn(notes, shift=UP * 0.1), run_time=theme.RUN)
        self.wait(4)
        self.play(FadeOut(title), FadeOut(rows), FadeOut(notes), run_time=theme.FAST)


class Creditos(Scene):
    def construct(self):
        self.camera.background_color = theme.BACKGROUND
        members_file = PROJECT_ROOT / "anim" / "integrantes.txt"
        members = [line.strip() for line in members_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        title = Text("DSU Tree: el DSU con memoria", font_size=48)
        team_label = Text("Integrantes", font_size=28, color=theme.DETAIL)
        team = VGroup(*[Text(name, font_size=30) for name in members]).arrange(DOWN, buff=0.2)
        info = VGroup(
            Text("CS2023 Algoritmos y Estructuras de Datos · UTEC 2026-2", font_size=22, color=theme.SECONDARY),
            Text("Prof. Wilder Nina Choquehuayta", font_size=22, color=theme.SECONDARY),
            Text("Animación con Manim Community Edition · estilo inspirado en 3Blue1Brown", font_size=22, color=theme.SECONDARY),
        ).arrange(DOWN, buff=0.15)
        block = VGroup(title, team_label, team, info).arrange(DOWN, buff=0.45)
        self.play(Write(title), run_time=1.2)
        self.play(FadeIn(team_label), LaggedStart(*[FadeIn(m, shift=UP * 0.1) for m in team], lag_ratio=0.3), run_time=1.5)
        self.play(FadeIn(info, shift=UP * 0.1), run_time=1)
        self.wait(5)
        self.play(FadeOut(block), run_time=1.2)
