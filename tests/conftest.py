import pytest

from echo_camera_assistant import Point


EXTENDED = {"open": 4, "fist": 0, "point": 1, "peace": 2, "thumb_up": 0, "thumb_down": 0,
            "pinch": 4, "pinch_wide": 4, "pinch_close": 4}
GESTURE_CATEGORIES = {
    "open": "Open_Palm",
    "fist": "Closed_Fist",
    "point": "Pointing_Up",
    "peace": "Victory",
    "thumb_up": "Thumb_Up",
    "thumb_down": "Thumb_Down",
    "pinch": "None",
    "pinch_wide": "None",
    "pinch_close": "None",
}


def build_hand(kind="open", x=0.5):
    if kind not in EXTENDED:
        return []
    hand = [Point(x, 0.7) for _ in range(21)]
    hand[0] = Point(x, 0.8)
    fingers = ((8, 6), (12, 10), (16, 14), (20, 18))
    for index, (offset, (tip, joint)) in enumerate(zip((-0.06, -0.02, 0.02, 0.06), fingers)):
        hand[joint] = Point(x + offset, 0.6)
        hand[tip] = Point(x + offset, 0.45 if index < EXTENDED[kind] else 0.72)
    if kind == "thumb_up":
        hand[2], hand[4] = Point(x - 0.08, 0.66), Point(x - 0.08, 0.45)
    elif kind == "thumb_down":
        hand[2], hand[4] = Point(x - 0.08, 0.76), Point(x - 0.08, 0.92)
    elif kind.startswith("pinch"):
        gap = {"pinch": 0.15, "pinch_wide": 0.65, "pinch_close": 0.02}[kind]
        hand[8] = Point(x - 0.06, 0.58)
        hand[4] = Point(x - 0.06 + gap * 0.1, 0.58)
    return hand


@pytest.fixture()
def hand_points():
    return build_hand


@pytest.fixture()
def camera_observation():
    def create(kind="open", lean=0.0, x=0.5):
        body = [Point(0.5, 0.5) for _ in range(33)]
        body[0] = Point(0.5, 0.2 + lean, 0)
        body[11], body[12] = Point(0.3, 0.5, 0.1), Point(0.7, 0.5, 0.1)
        if "+" in kind:
            left, right = kind.split("+", 1)
            hands = [("Left", left, build_hand(left, x - 0.15)), ("Right", right, build_hand(right, x + 0.15))]
        else:
            hands = [("Right", kind, build_hand(kind, x))]
        return body, [(side, points, GESTURE_CATEGORIES[name], 0.99) for side, name, points in hands if points]
    return create
