import os

from manim import (
    BLACK,
    BLUE_B,
    BLUE_C,
    BLUE_E,
    GOLD_C,
    GREEN_C,
    GREY_BROWN,
    RED_C,
    TEAL_C,
    WHITE,
    YELLOW_C,
    MathTex,
    Text,
)


def env_flag(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() not in ("0", "false", "no", "off", "")


SHOW_CAPTIONS = env_flag("DSU_CAPTIONS", True)

FONT = "CMU Serif"
Text.set_default(font=FONT)
MathTex.set_default(color=WHITE)

BACKGROUND = BLACK
TEXT_COLOR = WHITE
LEAF_STROKE = BLUE_C
LEAF_FILL = BLUE_E
LEAF_FILL_OPACITY = 0.5
DETAIL = BLUE_B
UNION_STROKE = YELLOW_C
ACCENT = GOLD_C
QUERY = RED_C
ANSWER = GREEN_C
ACTIVE = TEAL_C
SECONDARY = GREY_BROWN
EDGE_COLOR = WHITE

NODE_RADIUS = 0.42
NODE_STROKE = 4
HIGHLIGHT_STROKE = 7
EDGE_STROKE = 2.5
EDGE_OPACITY = 0.75
LABEL_SIZE = 34
UNION_LABEL_SIZE = 28

LEAF_SPACING = 1.6
LEVEL_HEIGHT = 1.3
TREE_BOTTOM = -2.05
TREE_MAX_WIDTH = 11.5

CAPTION_Y = 3.15
CAPTION_SIZE = 34
CAPTION_MAX_WIDTH = 12.5
FOOTER_SIZE = 20

RUN = 0.9
FAST = 0.6
PAUSE = 0.8
LONG_PAUSE = 1.6
