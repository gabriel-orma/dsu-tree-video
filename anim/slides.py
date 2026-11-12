from manim import (
    DOWN,
    LEFT,
    UP,
    FadeIn,
    FadeOut,
    LaggedStart,
    Mobject,
    Scene,
    Text,
    VGroup,
    Write,
)

import theme


def reading_time(*texts: str) -> float:
    words = sum(len(t.split()) for t in texts)
    return max(theme.READ_MIN, words * theme.READ_SECONDS_PER_WORD)


def heading(text: str, color=None) -> Text:
    title = Text(text, font_size=theme.HEADING_SIZE, color=color or theme.TEXT_COLOR)
    return title.to_edge(UP, buff=0.6)


def bullet_lines(lines: list[tuple[str, object]], size: int = theme.BODY_SIZE) -> VGroup:
    rows = VGroup(*[Text(text, font_size=size, color=color) for text, color in lines])
    rows.arrange(DOWN, aligned_edge=LEFT, buff=0.38)
    if rows.width > theme.CAPTION_MAX_WIDTH:
        rows.scale_to_fit_width(theme.CAPTION_MAX_WIDTH)
    return rows


def show_slide(scene: Scene, title: Text, body: Mobject, texts: list[str], extra_wait: float = 0.0) -> None:
    scene.play(Write(title), run_time=theme.FAST)
    parts = body.submobjects if isinstance(body, VGroup) and len(body.submobjects) > 1 else [body]
    reveal = theme.RUN + 0.3 * len(parts)
    scene.play(
        LaggedStart(*[FadeIn(part, shift=UP * 0.15) for part in parts], lag_ratio=0.35),
        run_time=reveal,
    )
    scene.wait(max(1.0, reading_time(*texts) - reveal / 2) + extra_wait)
    scene.play(FadeOut(title), FadeOut(body), run_time=theme.FAST)
