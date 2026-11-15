from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    LaggedStart,
    MathTex,
    RoundedRectangle,
    Scene,
    Text,
    TransformFromCopy,
    VGroup,
    Write,
    np,
)

import theme
from array_view import ArrayRow, MemoryView
from captions import Captions
from islands import IslandsView
from player import Narrator, TreePlayer
from slides import bullet_lines, heading, reading_time, show_slide
from step_player import StepPlayer
from trace_loader import PROJECT_ROOT, load_trace
from tree_view import HistoryTreeView, TreeBox, history_layout


def clear_scene(scene: Scene, run_time: float = theme.FAST) -> None:
    if scene.mobjects:
        scene.play(*[FadeOut(m) for m in scene.mobjects], run_time=run_time)


def merged_unions(events: list[dict]) -> list[dict]:
    return [e for e in events if e["op"] == "unite" and e["merged"]]


class Gancho(Scene):
    ISLANDS_LEFT = 3

    def construct(self):
        self.camera.background_color = theme.BACKGROUND
        events = load_trace("grande")
        n = events[0]["n"]
        narrator = Narrator(self, Captions())
        islands = IslandsView(n)

        narrator.play(
            LaggedStart(*[GrowFromCenter(islands.balls[x]) for x in range(1, n + 1)], lag_ratio=0.08),
            caption="Imagina elementos sueltos: personas, computadoras, ciudades…",
            run_time=1.8,
        )

        merges = merged_unions(events)
        stop = next(i for i, e in enumerate(merges) if len(set(e["comp"])) <= self.ISLANDS_LEFT)
        for i, event in enumerate(merges[: stop + 1]):
            narrator.play(
                *islands.apply_components(event["comp"]),
                caption="que poco a poco se van uniendo en grupos, como islas" if i == 0 else None,
                run_time=1.2 if i == 0 else 0.7,
            )
        narrator.say("Unir grupos y saber quién está con quién:\neso hace un DSU (Union-Find)")

        state = merges[stop]
        world = VGroup(islands.all_blobs(), islands.all_balls())
        narrator.play(
            world.animate.scale(0.7).shift(UP * 0.85),
            caption="Pero para la computadora, todo esto es solo un vector:",
        )

        cell = 0.85
        left_x = -n * cell / 2 + 0.6
        header = ArrayRow("x", list(range(1, n + 1)), left_x, -2.15, cell_width=cell, cell_height=0.55, is_header=True, text_size=32)
        padre = ArrayRow("padre[x]", state["padre"], left_x, -2.75, cell_width=cell, cell_height=0.55, text_size=32)
        self.play(
            LaggedStart(
                *[TransformFromCopy(islands.balls[x][1], header.texts[x - 1]) for x in range(1, n + 1)],
                lag_ratio=0.06,
            ),
            FadeIn(header.label),
            run_time=1.6,
        )
        narrator.play(
            padre.appear(),
            caption="padre[x]: cada elemento apunta a otro de su grupo",
            run_time=1.4,
        )

        roots = [x for x in range(1, n + 1) if state["padre"][x - 1] == x]
        root_marks = [m for x in roots for m in padre.mark(x, theme.ACCENT)]
        narrator.play(
            *root_marks,
            *[islands.balls[x][0].animate.set_stroke(theme.ACCENT, width=6) for x in roots],
            caption=f"si padre[x] = x, x es la raíz de su grupo: {len(roots)} raíces, {len(roots)} islas",
        )

        groups: dict[int, list[int]] = {}
        for x, root in enumerate(state["comp"], start=1):
            groups.setdefault(root, []).append(x)
        biggest_root = max(groups, key=lambda r: len(groups[r]))
        members = groups[biggest_root]
        member_marks = [m for x in members if x != biggest_root for m in padre.mark(x, theme.ACTIVE)]
        narrator.play(
            *member_marks,
            caption=f"una isla = las casillas que llegan a la misma raíz (aquí, la raíz {biggest_root})",
        )
        self.wait(0.4)
        clear_scene(self)


class Titulo(Scene):
    def construct(self):
        self.camera.background_color = theme.BACKGROUND
        title = Text("DSU Tree", font_size=theme.TITLE_SIZE)
        subtitle = Text("el DSU con memoria", font_size=40, color=theme.DETAIL)
        course = Text(
            "Proyecto Final 2 · CS2023 Algoritmos y Estructuras de Datos · UTEC 2026-2",
            font_size=24,
            color=theme.SECONDARY,
        )
        block = VGroup(title, subtitle, course).arrange(DOWN, buff=0.4)
        self.play(Write(title), run_time=1.2)
        self.play(FadeIn(subtitle, shift=UP * 0.2), FadeIn(course, shift=UP * 0.2), run_time=1.0)
        self.wait(2.2)
        self.play(FadeOut(block), run_time=theme.FAST)


class Pregunta(Scene):
    def construct(self):
        self.camera.background_color = theme.BACKGROUND
        query = next(e for e in load_trace("grande") if e["op"] == "query")
        lines = VGroup(
            Text("El vector padre[] solo guarda el presente:", font_size=36),
            Text("dice quién está con quién hoy, pero no desde cuándo.", font_size=36),
            Text(f"¿En qué momento se conectaron {query['a']} y {query['b']}?", font_size=40, color=theme.QUERY),
        ).arrange(DOWN, buff=0.45)
        self.play(FadeIn(lines[0], shift=UP * 0.15), run_time=theme.FAST)
        self.play(FadeIn(lines[1], shift=UP * 0.15), run_time=theme.FAST)
        self.wait(max(1.0, reading_time(lines[0].text, lines[1].text) - 1.5))
        self.play(Write(lines[2]), run_time=1.2)
        self.wait(1.4)
        follow = Text(
            "Para responder, hay que guardar el historial de uniones. ¿Cómo?",
            font_size=34,
            color=theme.ACCENT,
        ).next_to(lines, DOWN, buff=0.7)
        self.play(FadeIn(follow, shift=UP * 0.15), run_time=theme.FAST)
        self.wait(reading_time(follow.text))
        clear_scene(self)

        events = load_trace("idea")
        layout = history_layout(events)
        view = HistoryTreeView(layout, TreeBox(center_x=0, bottom=-2.4, top=1.7, spacing=2.0, radius=0.45))
        player = TreePlayer(self, view, Captions())
        player.show_leaves("Idea: cada elemento es una hoja de un árbol")
        merges = merged_unions(events)
        first, *rest = merges
        player.grow(
            first,
            pre_caption=f"unite({first['a']}, {first['b']}): dos grupos se unen…",
            caption=f"…y creamos un nodo nuevo encima de ambos\nque anota el momento de la unión: t = {first['t']}",
        )
        for event in rest:
            player.grow(
                event,
                caption=f"unite({event['a']}, {event['b']}): otro nodo encima de los dos grupos, t = {event['t']}",
            )
        for event in events:
            if event["op"] == "query":
                player.query(
                    event,
                    caption=f"¿Cuándo se conectaron {event['a']} y {event['b']}?",
                    answer_caption=f"t crece al subir, así que lo dice su ancestro común más cercano: t = {event['answer']}",
                )
        player.say("Eso es un DSU Tree: un DSU que recuerda su historia")
        clear_scene(self)


class TDA(Scene):
    def construct(self):
        self.camera.background_color = theme.BACKGROUND
        ops = [
            ("DSUTree(n)", "n elementos, cada uno en su propia componente"),
            ("unite(a, b)", "une sus componentes y registra el momento t"),
            ("connected(a, b)", "¿están hoy en la misma componente?"),
            ("whenConnected(a, b)", "momento t en que se conectaron (−1 si nunca)"),
        ]
        rows = VGroup()
        for signature, meaning in ops:
            rows.add(VGroup(
                Text(signature, font=theme.MONO_FONT, font_size=26, color=theme.UNION_STROKE),
                Text(meaning, font_size=26),
            ))
        sig_width = max(row[0].width for row in rows)
        for row in rows:
            row[1].next_to(row[0], RIGHT, buff=0.5)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        left_edge = rows.get_left()[0]
        for row in rows:
            row[0].align_to(np.array([left_edge, 0, 0]), LEFT)
            row[1].align_to(np.array([left_edge + sig_width + 0.5, 0, 0]), LEFT)
        box = RoundedRectangle(width=rows.width + 0.8, height=rows.height + 0.6, corner_radius=0.15)
        box.set_stroke(theme.SECONDARY, width=1.5)
        rows.move_to(box)
        label = Text("TDA: conectividad incremental con historia", font_size=24, color=theme.SECONDARY)
        uses = bullet_lines([
            ("Redes que se conectan con el tiempo: ¿desde cuándo hay conexión?", theme.TEXT_COLOR),
            ("Árbol de reconstrucción de Kruskal: arista más pesada entre a y b en el MST.", theme.TEXT_COLOR),
            ("Consultas offline de conectividad sobre una secuencia de uniones.", theme.TEXT_COLOR),
        ], size=26)
        uses_title = Text("¿Para qué se usa?", font_size=30, color=theme.DETAIL)
        body = VGroup(
            VGroup(label, VGroup(box, rows)).arrange(DOWN, buff=0.2),
            VGroup(uses_title, uses).arrange(DOWN, aligned_edge=LEFT, buff=0.25),
        ).arrange(DOWN, buff=0.5)
        if body.height > 5.6:
            body.scale_to_fit_height(5.6)
        body.move_to(DOWN * 0.55)
        show_slide(
            self,
            heading("DSU Tree: operaciones y usos"),
            body,
            [label.text] + [f"{s} {m}" for s, m in ops] + [uses_title.text] + [t.text for t in uses],
        )


class PasoAPaso(Scene):
    def construct(self):
        self.camera.background_color = theme.BACKGROUND
        events = load_trace("paso")
        n = events[0]["n"]
        layout = history_layout(events)
        view = HistoryTreeView(
            layout,
            TreeBox(
                center_x=4.15,
                max_width=4.4,
                bottom=-3.0,
                top=1.9,
                spacing=1.1,
                radius=0.3,
                show_ids=True,
                label_size=26,
                union_label_size=24,
            ),
        )
        memory = MemoryView(events[0], n, left_x=-4.9, top_y=2.2)
        captions = Captions()
        step = StepPlayer(self, view, memory, captions, full_unions={1, 3})

        step.play(
            FadeIn(memory.dsu_title),
            memory.x_index.appear(),
            memory.rows["padre"].appear(),
            memory.rows["tam"].appear(),
            memory.rows["nodo"].appear(),
            caption="Los vectores de la implementación. DSU auxiliar: padre[x] y tam[x] como siempre;\nnodo[x] = qué nodo del árbol representa a la componente (vale en las raíces)",
            run_time=1.4,
        )
        step.play(
            FadeIn(memory.tree_title),
            *[row.appear() for row in memory.tree_group()],
            step.leaves_animation(),
            caption=f"árbol de historia, 2n − 1 = {memory.slots} casillas (las hojas 1 … n ya existen): padreÁrbol[v] = padre de v,\n" + "t[v] = momento en que nació v, hijoIzq[v] e hijoDer[v] = los nodos que unió",
            run_time=1.4,
        )
        step.run(events)
        step.play(*captions.clear(), *step.reset_all(), run_time=theme.FAST)
        clear_scene(self)


class Grande(Scene):
    def construct(self):
        self.camera.background_color = theme.BACKGROUND
        events = load_trace("grande")
        layout = history_layout(events)
        view = HistoryTreeView(
            layout,
            TreeBox(center_x=0, max_width=12.2, bottom=-3.1, top=2.4, spacing=1.1, radius=0.34, label_size=24, union_label_size=22),
        )
        player = TreePlayer(self, view, Captions(), speed=0.4)
        player.say("Ahora el ejemplo de las islas completo, sin pausas")
        player.show_leaves()
        player.run_quiet(events)
        player.play(*player.captions.clear(), run_time=theme.FAST)
        self.wait(1.2)
        clear_scene(self)


class Complejidad(Scene):
    def construct(self):
        self.camera.background_color = theme.BACKGROUND
        events = load_trace("cadena")
        view = HistoryTreeView(history_layout(events), TreeBox(center_x=0, bottom=-2.8, top=2.2, spacing=1.6))
        player = TreePlayer(self, view, Captions(), speed=0.35)
        player.say("Peor caso para la consulta: una cadena de uniones", color=theme.QUERY)
        player.show_leaves()
        player.run_quiet(events)
        player.say("la altura llega a n − 1, así que whenConnected puede subir O(n) nodos", color=theme.QUERY)
        clear_scene(self)

        title = heading("Complejidad")
        rows_data = [
            ("unite(a, b)", r"O(\alpha(n))\ \text{amortizado}", "dos find + O(1) para crear el nodo nuevo"),
            ("connected(a, b)", r"O(\alpha(n))\ \text{amortizado}", "dos find en el DSU auxiliar"),
            ("whenConnected(a, b)", r"O(h) \le O(n)", "sube por el árbol de historia; h es su altura"),
            ("memoria", r"O(n)", "2n − 1 casillas en los vectores del árbol"),
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
            if row[2].width > 5.6:
                row[2].scale_to_fit_width(5.6)
            for col, mob in enumerate(row):
                mob.move_to(np.array([col_x[col], 1.6 - i * 0.95, 0]), aligned_edge=LEFT)
        notes = VGroup(
            MathTex(r"\alpha(n) \le 4 \text{ para cualquier } n \text{ práctico}", font_size=30, color=theme.DETAIL),
            Text("Mejora posible: saltos binarios (binary lifting) → O(log n) por consulta.", font_size=24, color=theme.SECONDARY),
        ).arrange(DOWN, buff=0.3).to_edge(DOWN, buff=0.9)

        self.play(Write(title), run_time=theme.FAST)
        for row in rows:
            self.play(LaggedStart(*[FadeIn(m, shift=RIGHT * 0.1) for m in row], lag_ratio=0.25), run_time=1.1)
            self.wait(reading_time(row[0].text, row[2].text))
        self.play(FadeIn(notes, shift=UP * 0.1), run_time=theme.FAST)
        self.wait(3.5)
        clear_scene(self)


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
