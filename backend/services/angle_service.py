from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: float
    y: float
    visibility: float = 1.0


def angle(a: Point, b: Point, c: Point) -> float:
    """Return angle ABC in degrees."""
    ab = (a.x - b.x, a.y - b.y)
    cb = (c.x - b.x, c.y - b.y)
    dot = ab[0] * cb[0] + ab[1] * cb[1]
    mag_ab = math.hypot(*ab)
    mag_cb = math.hypot(*cb)
    if mag_ab == 0 or mag_cb == 0:
        return 0.0
    cosine = max(-1.0, min(1.0, dot / (mag_ab * mag_cb)))
    return math.degrees(math.acos(cosine))


def vertical_torso_angle(shoulder: Point, hip: Point) -> float:
    """Return torso lean angle from the vertical axis in degrees."""
    dx = shoulder.x - hip.x
    dy = shoulder.y - hip.y
    if dx == 0 and dy == 0:
        return 0.0
    return abs(math.degrees(math.atan2(dx, -dy)))
