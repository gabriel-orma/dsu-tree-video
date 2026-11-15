from manim import (
    Animation,
    Circle,
    FadeIn,
    FadeOut,
    MathTex,
    ReplacementTransform,
    VGroup,
    np,
)

import theme

GOLDEN_ANGLE = np.pi * (3 - np.sqrt(5))


def scatter_positions(n: int, bounds: tuple[float, float, float, float], seed: int, min_gap: float) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    x0, x1, y0, y1 = bounds
    points: list[np.ndarray] = []
    attempts = 0
    while len(points) < n:
        attempts += 1
        candidate = np.array([rng.uniform(x0, x1), rng.uniform(y0, y1), 0.0])
        if all(np.linalg.norm(candidate - p) >= min_gap for p in points) or attempts > 20000:
            points.append(candidate)
    return points


def ball(label: int, radius: float = theme.BALL_RADIUS) -> VGroup:
    circle = Circle(radius=radius)
    circle.set_stroke(theme.LEAF_STROKE, width=3)
    circle.set_fill(theme.LEAF_FILL, opacity=theme.LEAF_FILL_OPACITY)
    text = MathTex(str(label), font_size=round(26 * radius / theme.BALL_RADIUS))
    circle.set_z_index(3)
    text.set_z_index(4)
    return VGroup(circle, text)


def packed_offsets(count: int, radius: float = theme.BALL_RADIUS) -> list[np.ndarray]:
    spacing = 2 * radius + 0.1
    offsets = [np.zeros(3)]
    ring = 1
    while len(offsets) < count:
        slots = 6 * ring
        for k in range(slots):
            angle = 2 * np.pi * k / slots + ring * 0.3
            offsets.append(ring * spacing * np.array([np.cos(angle), np.sin(angle), 0.0]))
        ring += 1
    return offsets[:count]


class IslandsView:
    def __init__(
        self,
        n: int,
        bounds=(-6.2, 6.2, -2.7, 2.3),
        seed: int = 11,
        radius: float = theme.BALL_RADIUS,
        min_gap: float = 1.15,
    ):
        self.n = n
        self.bounds = bounds
        self.radius = radius
        start = scatter_positions(n, bounds, seed, min_gap)
        self.pos = {x: start[x - 1] for x in range(1, n + 1)}
        self.balls = {x: ball(x, radius).move_to(self.pos[x]) for x in range(1, n + 1)}
        self.groups: dict[frozenset, np.ndarray] = {frozenset([x]): self.pos[x].copy() for x in range(1, n + 1)}
        self.blobs: dict[frozenset, Circle] = {}

    def radius_for(self, size: int) -> float:
        if size == 1:
            return self.radius
        reach = max(np.linalg.norm(o) for o in packed_offsets(size, self.radius))
        return reach + self.radius + 0.2

    def blob(self, members: frozenset, center: np.ndarray) -> Circle:
        shape = Circle(radius=self.radius_for(len(members)))
        shape.set_stroke(theme.ISLAND_COLOR, width=2.5)
        shape.set_fill(theme.ISLAND_COLOR, opacity=0.12)
        shape.set_z_index(1)
        return shape.move_to(center)

    def separate(self, centers: dict[frozenset, np.ndarray], fixed: frozenset | None) -> None:
        x0, x1, y0, y1 = self.bounds
        keys = list(centers)
        for _ in range(200):
            moved = False
            for i, a in enumerate(keys):
                for b in keys[i + 1 :]:
                    delta = centers[b] - centers[a]
                    dist = np.linalg.norm(delta)
                    need = self.radius_for(len(a)) + self.radius_for(len(b)) + 0.25
                    if dist < need:
                        direction = delta / dist if dist > 1e-6 else np.array([1.0, 0.0, 0.0])
                        push = (need - dist) / 2
                        if a == fixed:
                            centers[b] = centers[b] + direction * 2 * push
                        elif b == fixed:
                            centers[a] = centers[a] - direction * 2 * push
                        else:
                            centers[a] = centers[a] - direction * push
                            centers[b] = centers[b] + direction * push
                        moved = True
            for key in keys:
                r = self.radius_for(len(key))
                centers[key][0] = min(max(centers[key][0], x0 + r), x1 - r)
                centers[key][1] = min(max(centers[key][1], y0 + r), y1 - r)
            if not moved:
                break

    def apply_components(self, comp: list[int]) -> list[Animation]:
        members: dict[int, list[int]] = {}
        for x, root in enumerate(comp, start=1):
            members.setdefault(root, []).append(x)
        new_groups = [frozenset(m) for m in members.values()]
        centers: dict[frozenset, np.ndarray] = {}
        merged: frozenset | None = None
        for group in new_groups:
            if group in self.groups:
                centers[group] = self.groups[group].copy()
            else:
                parts = [old for old in self.groups if old <= group]
                weights = np.array([len(p) for p in parts], dtype=float)
                stacked = np.array([self.groups[p] for p in parts])
                centers[group] = (stacked * weights[:, None]).sum(axis=0) / weights.sum()
                merged = group
        self.separate(centers, merged)

        animations: list[Animation] = []
        for group, center in centers.items():
            ordered = sorted(group)
            for x, offset in zip(ordered, packed_offsets(len(ordered), self.radius)):
                target = center + offset
                if np.linalg.norm(target - self.pos[x]) > 1e-3:
                    animations.append(self.balls[x].animate.move_to(target))
                self.pos[x] = target
            if len(group) > 1:
                new_blob = self.blob(group, center)
                if group in self.blobs:
                    animations.append(self.blobs[group].animate.move_to(center))
                else:
                    olds = [self.blobs.pop(old) for old in list(self.blobs) if old <= group]
                    if olds:
                        animations.append(ReplacementTransform(VGroup(*olds), new_blob))
                    else:
                        animations.append(FadeIn(new_blob, scale=0.6))
                    self.blobs[group] = new_blob
        self.groups = centers
        return animations

    def all_balls(self) -> VGroup:
        return VGroup(*[self.balls[x] for x in range(1, self.n + 1)])

    def all_blobs(self) -> VGroup:
        return VGroup(*self.blobs.values())

    def fade_blobs(self) -> list[Animation]:
        return [FadeOut(b) for b in self.blobs.values()]
