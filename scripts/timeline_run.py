import atexit
import json
import os
import sys

from manim import Scene
from manim.animation.animation import Animation
from manim.mobject.text.text_mobject import Text

OUT = os.environ["TIMELINE_OUT"]
log = []


def texts_in(anim):
    found = []
    name = type(anim).__name__
    if name in ("FadeOut", "Uncreate", "Unwrite"):
        return found
    subs = getattr(anim, "animations", None)
    if subs:
        for sub in subs:
            found += texts_in(sub)
        return found
    candidates = []
    target = getattr(anim, "target_mobject", None)
    if name in ("ReplacementTransform", "Transform", "TransformFromCopy") and target is not None:
        candidates.append(target)
    elif name in ("FadeIn", "Write", "GrowFromCenter", "AddTextLetterByLetter", "Create", "DrawBorderThenFill"):
        candidates.append(anim.mobject)
    for mob in candidates:
        for part in mob.get_family():
            if isinstance(part, Text) and getattr(part, "text", "").strip():
                found.append(part.text)
    return found


original_play = Scene.play
original_wait = Scene.wait


def play(self, *args, **kwargs):
    start = self.renderer.time
    texts = []
    for a in args:
        if isinstance(a, Animation):
            texts += texts_in(a)
    result = original_play(self, *args, **kwargs)
    log.append({"scene": type(self).__name__, "start": start, "end": self.renderer.time, "texts": texts})
    return result


def wait(self, *args, **kwargs):
    start = self.renderer.time
    result = original_wait(self, *args, **kwargs)
    log.append({"scene": type(self).__name__, "start": start, "end": self.renderer.time, "texts": [], "wait": True})
    return result


Scene.play = play
Scene.wait = wait


@atexit.register
def dump():
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(log, fh, ensure_ascii=False, indent=1)


from manim.__main__ import main

sys.argv = ["manim"] + sys.argv[1:]
main()
