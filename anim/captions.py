from manim import DOWN, UP, Animation, FadeIn, FadeOut, Text

import theme


class Captions:
    def __init__(self, enabled: bool | None = None):
        self.enabled = theme.SHOW_CAPTIONS if enabled is None else enabled
        self.current: Text | None = None

    def show(self, text: str, color=None) -> list[Animation]:
        if not self.enabled:
            return []
        caption = Text(
            text,
            font_size=theme.CAPTION_SIZE,
            color=color or theme.TEXT_COLOR,
            line_spacing=0.8,
        )
        if caption.width > theme.CAPTION_MAX_WIDTH:
            caption.scale_to_fit_width(theme.CAPTION_MAX_WIDTH)
        caption.move_to(UP * theme.CAPTION_Y)
        animations: list[Animation] = [FadeIn(caption, shift=DOWN * 0.15)]
        if self.current is not None:
            animations.append(FadeOut(self.current, shift=UP * 0.15))
        self.current = caption
        return animations

    def clear(self) -> list[Animation]:
        if not self.enabled or self.current is None:
            return []
        old = self.current
        self.current = None
        return [FadeOut(old, shift=UP * 0.15)]
