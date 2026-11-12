"""Local posture reminders and explicitly armed hand gestures."""

import ctypes
import hashlib
import logging
import math
import os
import statistics
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from contextlib import ExitStack
from collections import deque
from collections.abc import Callable
from ctypes import wintypes
from dataclasses import asdict, dataclass, field
from itertools import product
from pathlib import Path

from echo_presence import CameraSource, PresenceError


LOGGER = logging.getLogger(__name__)
GESTURE_FRAME_SECONDS = 1 / 20
POSTURE_FRAME_SECONDS = 1 / 5
HOLD_SECONDS = 0.8
PAIR_HOLD_SECONDS = 1.0
REPEAT_START_SECONDS = 0.6
REPEAT_SECONDS = 0.3
ACTION_COOLDOWN_SECONDS = 2.0
MOTION_WINDOW_SECONDS = 1.2
TIME_EPSILON = 1e-6
MATCH_DISTANCE = 0.3
MATCH_MARGIN = 0.1
MIN_FINGER_SPAN = 0.35
RELATIVE_MATCH_DISTANCE = 0.35
RELATIVE_MATCH_MARGIN = 0.15
TRACK_GRACE_SECONDS = 0.18
TRACK_MATCH_DISTANCE = 0.2
TRACK_AMBIGUITY_MARGIN = 0.04
TRACK_MAX_SAME_SIDE_DISTANCE = 0.45
RELEASE_CONFIRM_SECONDS = 0.15
GESTURE_MIN_CONFIDENCE = 0.6
OPEN_HAND_MIN_EXTENSION = 1.25
PINCH_START_RATIO = 0.3
PINCH_END_RATIO = 1.2
PINCH_STEP_RATIO = 0.12
PINCH_HOLD_SECONDS = 0.4
POINT_STILL_DISTANCE = 0.1
PRETRAINED_GESTURES = {
    "Open_Palm": "open",
    "Closed_Fist": "fist",
    "Pointing_Up": "point",
    "Victory": "peace",
    "Thumb_Up": "thumb_up",
    "Thumb_Down": "thumb_down",
}
HOLD_ACTIONS = {"fist": "mute", "point": "play_pause", "peace": "show_desktop"}
REPEAT_ACTIONS = {"thumb_up": "volume_up", "thumb_down": "volume_down"}
EXTRA_KEYS = {
    "play_pause": ("playpause",),
    "show_desktop": ("win", "d"),
    "volume_up": ("volumeup",),
    "volume_down": ("volumedown",),
    "speaker_mute": ("volumemute",),
    "zoom_in": ("ctrl", "add"),
    "zoom_out": ("ctrl", "subtract"),
}
MODEL_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "Echo" / "models"
MODELS = {
    "gesture": (
        "gesture_recognizer.task",
        "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task",
        "97952348cf6a6a4915c2ea1496b4b37ebabc50cbbf80571435643c455f2b0482",
    ),
    "pose": (
        "pose_landmarker_lite.task",
        "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
        "59929e1d1ee95287735ddd833b19cf4ac46d29bc7afddbbf6753c459690d574a",
    ),
}
ERRORS = {
    "settings": ("Invalid camera assistant settings.", "Ongeldige instellingen voor de camera-assistent."),
    "dependency": ("Restart Echo after installing requirements.txt.", "Herstart Echo na installatie van requirements.txt."),
    "models": ("Cannot download or verify the local vision models. Check your internet connection and disk permissions.", "De lokale modellen kunnen niet worden gedownload of gecontroleerd. Controleer internet en schrijfrechten."),
    "vision": ("Local landmark detection failed. Stop and restart the camera assistant.", "Lokale herkenning mislukt. Stop en herstart de camera-assistent."),
    "running": ("Stop the camera assistant before changing settings.", "Stop de camera-assistent voordat je instellingen wijzigt."),
    "inactive": ("Start the camera assistant first.", "Start eerst de camera-assistent."),
    "training": ("Scan your open hand before enabling actions.", "Scan eerst je open hand voordat je acties activeert."),
    "microphone": ("Cannot access the selected Windows microphone. Check the device and permissions.", "De gekozen Windows-microfoon is niet bereikbaar. Controleer het apparaat en de rechten."),
    "action": ("Windows could not execute the gesture action. Actions have been disabled.", "Windows kon de gebaaractie niet uitvoeren. Acties zijn uitgeschakeld."),
    "locked": ("Actions are unavailable on the lock screen.", "Acties zijn niet beschikbaar op het vergrendelscherm."),
}


class CameraAssistantError(Exception):
    def __init__(self, code: str, status: int = 503):
        self.code = code
        self.status = status
        super().__init__(ERRORS[code][0])

    def localized(self, dutch: bool) -> str:
        return ERRORS[self.code][int(dutch)]


@dataclass(frozen=True)
class Settings:
    camera_index: int = 0
    posture: bool = True
    gestures: bool = True
    delay_seconds: int = 30
    swipe_action: str = "media"
    microphone: str = "communications"
    sound: bool = False
    extra_gestures: bool = True

    @classmethod
    def parse(cls, data: object) -> "Settings":
        if not isinstance(data, dict) or set(data) != set(cls.__dataclass_fields__):
            raise CameraAssistantError("settings", 400)
        if (
            type(data["camera_index"]) is not int or not 0 <= data["camera_index"] <= 10
            or type(data["delay_seconds"]) is not int or not 10 <= data["delay_seconds"] <= 300
            or any(type(data[key]) is not bool for key in ("posture", "gestures", "sound", "extra_gestures"))
            or not (data["posture"] or data["gestures"])
            or data["swipe_action"] not in ("media", "desktop")
            or not isinstance(data["microphone"], str) or not 1 <= len(data["microphone"]) <= 256
        ):
            raise CameraAssistantError("settings", 400)
        return cls(**data)


def ensure_model(kind: str) -> Path:
    filename, url, expected_hash = MODELS[kind]
    target = MODEL_DIR / filename
    temporary = None
    try:
        if target.is_file() and target.stat().st_size <= 16 * 1024 * 1024 and hashlib.sha256(target.read_bytes()).hexdigest() == expected_hash:
            return target
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256()
        size = 0
        with urllib.request.urlopen(url, timeout=30) as response:
            with tempfile.NamedTemporaryFile(dir=MODEL_DIR, suffix=".download", delete=False) as output:
                temporary = Path(output.name)
                while chunk := response.read(64 * 1024):
                    size += len(chunk)
                    if size > 16 * 1024 * 1024:
                        raise CameraAssistantError("models")
                    digest.update(chunk)
                    output.write(chunk)
        if digest.hexdigest() != expected_hash:
            raise CameraAssistantError("models")
        os.replace(temporary, target)
        return target
    except (OSError, urllib.error.URLError, TimeoutError) as exc:
        raise CameraAssistantError("models") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


@dataclass(frozen=True)
class Point:
    x: float
    y: float
    z: float = 0
    visibility: float = 1


def posture_features(points: list[Point]) -> tuple[float, ...] | None:
    if len(points) != 33:
        return None
    nose, left, right = points[0], points[11], points[12]
    if any(not math.isfinite(p.visibility) or p.visibility < 0.7 or not 0 <= p.x <= 1 or not 0 <= p.y <= 1 for p in (nose, left, right)):
        return None
    span = math.hypot(left.x - right.x, left.y - right.y)
    if span < 0.08:
        return None
    values = ((nose.y - (left.y + right.y) / 2) / span, ((left.z + right.z) / 2 - nose.z) / span)
    return values if all(math.isfinite(value) for value in values) else None


def hand_features(points: list[Point]) -> tuple[float, ...] | None:
    if len(points) != 21 or any(not 0 <= p.x <= 1 or not 0 <= p.y <= 1 for p in points):
        return None
    wrist = points[0]
    values = []
    for tip, joint in ((8, 6), (12, 10), (16, 14), (20, 18)):
        denominator = math.dist(point_coordinates(points[joint]), point_coordinates(wrist))
        if denominator < 0.02:
            return None
        values.append(math.dist(point_coordinates(points[tip]), point_coordinates(wrist)) / denominator)
    return tuple(values) if all(math.isfinite(value) for value in values) else None


def point_coordinates(point: Point) -> tuple[float, float, float]:
    return point.x, point.y, point.z


def pinch_gap(points: list[Point]) -> float | None:
    values = hand_features(points)
    if values is None or any(value < OPEN_HAND_MIN_EXTENSION for value in values[1:]):
        return None
    if any(
        not all(math.isfinite(value) for value in point_coordinates(point))
        or not math.isfinite(point.visibility) or point.visibility < 0.7
        for point in points
    ):
        return None
    palm = math.dist(point_coordinates(points[0]), point_coordinates(points[9]))
    if palm < 0.04:
        return None
    return math.dist(point_coordinates(points[4]), point_coordinates(points[8])) / palm


def thumb_direction(points: list[Point]) -> str:
    if len(points) != 21 or any(not (math.isfinite(p.x) and math.isfinite(p.y)) for p in points):
        return ""
    palm = math.hypot(points[9].x - points[0].x, points[9].y - points[0].y)
    if palm < 0.03:
        return ""
    base, tip = points[2], points[4]
    dx, dy = tip.x - base.x, tip.y - base.y
    if abs(dy) < 0.35 * palm or abs(dx) > 0.8 * abs(dy):
        return ""
    # The thumb tip must clear the wrist and every finger, so a tucked thumb stays a fist.
    others = [p.y for index, p in enumerate(points) if index == 0 or index > 4]
    if dy < 0 and tip.y <= min(others) - 0.15 * palm:
        return "up"
    if dy > 0 and tip.y >= max(others) + 0.15 * palm:
        return "down"
    return ""


@dataclass(frozen=True)
class HandObservation:
    identity: str
    values: tuple[float, ...] | None
    x: float
    y: float
    thumb: str = ""
    category: str | None = None
    confidence: float = 0.0
    pinch: float | None = None

    @classmethod
    def from_points(
        cls, identity: str, points: list[Point], category: str | None = None, confidence: float = 0.0
    ) -> "HandObservation":
        wrist = points[0] if points else Point(0, 0)
        return cls(identity, hand_features(points), wrist.x, wrist.y, thumb_direction(points), category, confidence, pinch_gap(points))


@dataclass
class HandState:
    label: str = "unknown"
    since: float | None = None
    motion: deque[tuple[float, float, float]] = field(default_factory=lambda: deque(maxlen=64))
    fired: bool = False
    fired_label: str = ""
    next_repeat: float = 0.0
    uncertain: bool = False
    last_confident: float = -math.inf
    last_seen: float = -math.inf
    last_observed: float | None = None
    position: tuple[float, float] | None = None
    release_label: str = ""
    release_since: float | None = None
    hold_origin: tuple[float, float] | None = None
    pinch_samples: deque[float] = field(default_factory=lambda: deque(maxlen=3))
    pinch_anchor: float | None = None

    def reset(self, label: str, preserve_latch: bool = False) -> None:
        self.label = label
        self.since = None
        self.motion.clear()
        if not preserve_latch:
            self.fired_label = ""
            self.release_label = ""
            self.release_since = None
        self.fired = bool(self.fired_label)
        self.next_repeat = 0.0
        self.uncertain = False
        self.last_confident = self.last_seen = -math.inf
        self.last_observed = None
        self.hold_origin = None
        self.pinch_samples.clear()
        self.pinch_anchor = None

    def pause(self, now: float) -> None:
        if self.label == "pinch":
            self.pinch_samples.clear()
            self.pinch_anchor = None
            self.since = None
            return
        if self.since is not None and self.last_observed is not None:
            self.since += max(0.0, now - self.last_observed)


def trim_motion(motion: deque, now: float) -> None:
    while motion and now - motion[0][0] > MOTION_WINDOW_SECONDS:
        motion.popleft()


class Calibration:
    def __init__(self, target: str, now: float):
        self.target = target
        self.deadline = now + 15
        self.samples: list[tuple[float, ...]] = []
        self.since: float | None = None
        self.last = now
        self.progress = 0
        self.duration = 1 if target == "activate" else 2
        self.minimum_samples = 5 if target == "activate" else 10

    def observe(self, values: tuple[float, ...] | None, now: float) -> tuple[float, ...] | None:
        valid = values is not None
        if values is not None and self.target in {"open", "fist"}:
            valid = sum(value > 1.15 if self.target == "open" else value < 1.05 for value in values) >= 3
        if not valid or now - self.last > 0.5:
            self.samples.clear()
            self.since = None
            self.progress = 0
        self.last = now
        if not valid or values is None:
            return None
        if self.since is None:
            self.since = now
        self.samples.append(values)
        self.progress = min(100, int((now - self.since) * 100 / self.duration))
        if now - self.since + TIME_EPSILON >= self.duration and len(self.samples) >= self.minimum_samples:
            return tuple(statistics.median(column) for column in zip(*self.samples))
        return None


class PostureTracker:
    def __init__(self, delay: int):
        self.delay = delay
        self.baseline: tuple[float, ...] | None = None
        self.since: float | None = None
        self.last = 0.0
        self.last_alert = -math.inf
        self.phase = "needs_calibration"

    def observe(self, values: tuple[float, ...] | None, now: float) -> bool:
        if now - self.last > 0.5:
            self.since = None
        self.last = now
        if values is None or self.baseline is None:
            self.since = None
            self.phase = "no_pose" if values is None else "needs_calibration"
            return False
        leaning = values[0] - self.baseline[0] >= 0.18 or values[1] - self.baseline[1] >= 0.25
        self.phase = "leaning" if leaning else "upright"
        if not leaning:
            self.since = None
            return False
        if self.since is None:
            self.since = now
        if now - self.since >= self.delay and now - self.last_alert >= 120:
            self.last_alert = now
            return True
        return False


class GestureTracker:
    def __init__(self, extra: bool = True):
        self.examples: dict[str, tuple[float, ...]] = {}
        self.scanned = False
        self.extra = extra
        self.armed = False
        self.label = "unknown"
        self.last = 0.0
        self.cooldown = 0.0
        self.hands: dict[str, HandState] = {}
        self.visible: list[tuple[str, str]] = []
        self.pair_label = ""
        self.pair_ids: tuple[str, ...] = ()
        self.pair_since: float | None = None
        self.pair_motion: deque[tuple[float, float, float, float, float]] = deque(maxlen=64)
        self.pair_fired = False
        self.pair_uncertain = False
        self.pair_latch: tuple[str, tuple[str, ...]] | None = None

    @property
    def ready(self) -> bool:
        return self.scanned or {"open", "fist"} <= self.examples.keys()

    def reset_motion(self) -> None:
        self.hands.clear()
        self.visible = []
        self._reset_pair("", ())
        self.pair_latch = None
        self.label = "unknown"

    def _reset_pair(self, label: str, ids: tuple[str, ...]) -> None:
        self.pair_label, self.pair_ids = label, ids
        self.pair_since = None
        self.pair_motion.clear()
        self.pair_fired = False
        self.pair_uncertain = False

    def hand_labels(self) -> list[dict[str, str | bool]]:
        return [
            {"side": side, "gesture": label, "needs_release": self.hands[side].fired}
            for side, label in self.visible
        ]

    def templates(self) -> dict[str, tuple[float, ...]]:
        templates = dict(self.examples)
        if self.extra and {"open", "fist"} <= set(templates):
            opened, closed = templates["open"], templates["fist"]
            # Extra shapes reuse the personal open/fist examples per finger instead of separate training.
            for name, shape in (("point", (opened[0], *closed[1:])), ("peace", (*opened[:2], *closed[2:]))):
                if all(max(abs(a - b) for a, b in zip(shape, other)) >= MATCH_DISTANCE for other in templates.values()):
                    templates[name] = shape
        return templates

    def classify(self, hand: HandObservation, pinching: bool = False) -> str:
        if (
            not math.isfinite(hand.x) or not math.isfinite(hand.y)
            or not 0 <= hand.x <= 1 or not 0 <= hand.y <= 1
            or (hand.category is not None and (not math.isfinite(hand.confidence) or not 0 <= hand.confidence <= 1))
        ):
            return "unknown"
        if (
            self.extra and hand.pinch is not None and math.isfinite(hand.pinch)
            and 0 <= hand.pinch <= (PINCH_END_RATIO if pinching else PINCH_START_RATIO)
        ):
            return "pinch"
        if hand.category is not None:
            if (
                hand.category in {"", "None", "Open_Palm"} and hand.values is not None
                and len(hand.values) == 4
                and all(math.isfinite(value) and value >= OPEN_HAND_MIN_EXTENSION for value in hand.values)
            ):
                return "open"
            if hand.confidence < GESTURE_MIN_CONFIDENCE:
                return "unknown"
            label = PRETRAINED_GESTURES.get(hand.category, "unknown")
            return label if self.extra or label in {"open", "fist"} else "unknown"
        if hand.values is None or len(hand.values) != 4 or not all(math.isfinite(value) for value in hand.values):
            return "unknown"
        templates = self.templates()
        distances = sorted(
            (max(abs(a - b) for a, b in zip(hand.values, example)), label)
            for label, example in templates.items()
        )
        label = self._best_match(distances, MATCH_DISTANCE, MATCH_MARGIN)
        if not label and {"open", "fist"} <= self.examples.keys():
            opened, closed = self.examples["open"], self.examples["fist"]
            spans = tuple(a - b for a, b in zip(opened, closed))
            if len(spans) == 4 and all(span >= MIN_FINGER_SPAN for span in spans):
                relative = sorted(
                    (max(abs(value - example[i]) / spans[i] for i, value in enumerate(hand.values)), name)
                    for name, example in templates.items()
                )
                label = self._best_match(relative, RELATIVE_MATCH_DISTANCE, RELATIVE_MATCH_MARGIN)
        if not label:
            return "unknown"
        if label == "fist" and self.extra and hand.thumb in {"up", "down"}:
            return "thumb_" + hand.thumb
        return label

    @staticmethod
    def _best_match(distances: list[tuple[float, str]], limit: float, margin: float) -> str:
        if not distances or distances[0][0] > limit:
            return ""
        if len(distances) > 1 and distances[1][0] - distances[0][0] < margin:
            return ""
        return distances[0][1]

    def _associate_hands(
        self, hands: list[HandObservation], now: float
    ) -> tuple[list[tuple[HandObservation, HandState]], bool]:
        previous = {
            identity: state for identity, state in self.hands.items()
            if state.position is not None and now - state.last_seen <= TRACK_GRACE_SECONDS
        }
        options: tuple[str | None, ...] = (None, *previous)
        assignments: list[tuple[int, float, tuple[str | None, ...]]] = []
        for identities in product(options, repeat=len(hands)):
            matched = [identity for identity in identities if identity is not None]
            if len(set(matched)) != len(matched):
                continue
            distances = []
            for hand, identity in zip(hands, identities):
                if identity is not None:
                    state = previous[identity]
                    distance = math.dist((hand.x, hand.y), state.position)
                    limit = TRACK_MATCH_DISTANCE
                    if hand.identity == identity:
                        limit = math.inf if len(hands) == len(previous) == 1 else TRACK_MAX_SAME_SIDE_DISTANCE
                    if distance > limit:
                        break
                    distances.append(distance)
            else:
                assignments.append((len(matched), sum(distances), identities))
        assignments.sort(key=lambda item: (-item[0], item[1]))
        best = assignments[0]
        ambiguous = (
            len(assignments) > 1 and best[0] > 0 and assignments[1][0] == best[0]
            and assignments[1][1] - best[1] < TRACK_AMBIGUITY_MARGIN
        )
        if len(hands) == 2 and math.dist((hands[0].x, hands[0].y), (hands[1].x, hands[1].y)) < TRACK_AMBIGUITY_MARGIN:
            ambiguous = True
        reserved = {identity for identity in best[2] if identity is not None}
        used: set[str] = set()
        associated = []
        for hand, identity in zip(hands, best[2]):
            if identity is None:
                identity = next(
                    candidate for candidate in (hand.identity, "Left", "Right", "Hand")
                    if candidate not in used and candidate not in reserved
                )
                state = HandState()
                old = self.hands.get(identity)
                if old and old.fired_label:
                    state.fired_label = old.fired_label
                    state.fired = True
            else:
                state = previous[identity]
            used.add(identity)
            associated.append((HandObservation(
                identity, hand.values, hand.x, hand.y, hand.thumb, hand.category, hand.confidence, hand.pinch
            ), state))
        return associated, ambiguous

    def observe(self, hands: list[HandObservation], now: float) -> str | None:
        previous_time = self.last
        if now - self.last > 0.5:
            self.hands = {identity: state for identity, state in self.hands.items() if state.fired_label}
            for state in self.hands.values():
                state.reset("unknown", preserve_latch=True)
                state.last_seen = now
            self.visible = []
            self._reset_pair("", ())
            self.label = "unknown"
        self.last = now
        visible: list[tuple[HandObservation, HandState]] = []
        observations = sorted(hands, key=lambda item: item.x)[:2]
        associated, ambiguous = self._associate_hands(observations, now)
        for hand, state in associated:
            label = "unknown" if ambiguous else self.classify(hand, state.label == "pinch")
            if state.fired_label:
                if label in {"unknown", state.fired_label}:
                    state.release_label = ""
                    state.release_since = None
                else:
                    if label != state.release_label:
                        state.release_label, state.release_since = label, now
                    if state.release_since is not None and now - state.release_since + TIME_EPSILON < RELEASE_CONFIRM_SECONDS:
                        label = "unknown"
            if label != "unknown":
                if label != state.label:
                    state.reset(label, preserve_latch=state.fired_label == label)
                elif state.uncertain:
                    state.pause(now)
                state.uncertain = False
                state.last_confident = now
                if state.since is None:
                    state.since = now
                if label == "point":
                    position = (hand.x, hand.y)
                    if state.hold_origin is None or math.dist(position, state.hold_origin) > POINT_STILL_DISTANCE:
                        state.hold_origin = position
                        state.since = now
                if label == "pinch" and hand.pinch is not None:
                    state.pinch_samples.append(hand.pinch)
                state.motion.append((now, hand.x, hand.y))
                trim_motion(state.motion, now)
            elif now - state.last_confident <= TRACK_GRACE_SECONDS:
                state.pause(now)
                state.uncertain = True
            else:
                state.reset("unknown", preserve_latch=True)
                state.uncertain = True
            state.last_seen = state.last_observed = now
            if not ambiguous or state.position is None:
                state.position = (hand.x, hand.y)
            visible.append((hand, state))
        tracked = {hand.identity: state for hand, state in visible}
        for identity, state in self.hands.items():
            if len(tracked) < 2 and identity not in tracked and now - state.last_seen <= TRACK_GRACE_SECONDS:
                state.pause(now)
                state.uncertain = True
                state.last_observed = now
                tracked[identity] = state
        self.hands = tracked
        self.visible = [(hand.identity, "unknown" if state.uncertain else state.label) for hand, state in visible]
        if self.pair_latch:
            latched_label, latched_ids = self.pair_latch
            if any(
                identity not in tracked or (
                    not tracked[identity].uncertain and tracked[identity].label != latched_label
                )
                for identity in latched_ids
            ):
                self.pair_latch = None
        pair_states = [state for _hand, state in visible]
        ids = tuple(sorted(hand.identity for hand, _state in visible))
        if len(visible) < 2 and self.pair_label and all(identity in tracked for identity in self.pair_ids):
            ids = self.pair_ids
            pair_states = [tracked[identity] for identity in ids]
        labels = [state.label for state in pair_states]
        pair = labels[0] if self.extra and len(labels) == 2 and labels[0] == labels[1] and labels[0] in {"open", "fist"} else ""
        pair_confident = bool(pair and len(visible) == 2 and all(not state.uncertain for state in pair_states))
        if pair != self.pair_label or ids != self.pair_ids:
            if self.pair_label == "fist" and pair != "fist":
                for _hand, state in visible:
                    if state.label == "fist" and not state.fired:
                        state.since = now
            self._reset_pair(pair, ids)
        if pair:
            if self.pair_since is None and pair_confident:
                self.pair_since = now
            elif self.pair_since is not None and (not pair_confident or self.pair_uncertain):
                self.pair_since += max(0.0, now - previous_time)
            self.pair_uncertain = not pair_confident
            if pair_confident:
                first, second = visible[0][0], visible[1][0]
                self.pair_motion.append((now, first.x, second.x, first.y, second.y))
                trim_motion(self.pair_motion, now)
        pinching = [state for state in tracked.values() if state.label == "pinch"]
        priority_label = "pinch" if any(not state.uncertain for state in pinching) else (
            {"open": "two_open", "fist": "two_fists"}.get(pair) if pair_confident else ""
        )
        self.label = priority_label or next(
            (label for _side, label in self.visible if label != "unknown"), "unknown"
        )
        if pinching:
            for _hand, state in visible:
                if state.label != "pinch":
                    state.since = now
                    state.motion.clear()
            if len(pinching) != 1 or pinching[0].uncertain:
                for state in pinching:
                    state.pause(now)
                return None
        if not self.armed or now + TIME_EPSILON < self.cooldown:
            return None
        if pinching:
            return self._pinch_action(pinching[0], now)
        if pair_confident and not self.pair_fired and not self.pair_latch:
            action = self._pair_action(now)
            if action:
                self.pair_fired = True
                self.pair_latch = (pair, ids)
                for _hand, state in visible:
                    state.fired = True
                    state.fired_label = state.label
                self.cooldown = now + ACTION_COOLDOWN_SECONDS
                return action
        for index, (_hand, state) in enumerate(visible):
            if pair == "fist":
                break
            other = visible[1 - index][1] if len(visible) == 2 else None
            if state.uncertain or (other and other.uncertain and state.label in {"open", "fist"}):
                continue
            action = self._hand_action(state, other, now)
            if action:
                return action
        return None

    def _pinch_action(self, state: HandState, now: float) -> str | None:
        if state.since is None or now - state.since + TIME_EPSILON < PINCH_HOLD_SECONDS or len(state.pinch_samples) < 3:
            return None
        gap = statistics.median(state.pinch_samples)
        if state.pinch_anchor is None:
            state.pinch_anchor = gap
            return None
        delta = gap - state.pinch_anchor
        if abs(delta) + TIME_EPSILON < PINCH_STEP_RATIO:
            return None
        state.pinch_anchor = gap
        self.cooldown = now + REPEAT_SECONDS
        return "volume_up" if delta > 0 else "volume_down"

    def _pair_action(self, now: float) -> str | None:
        if self.pair_since is None or not self.pair_motion:
            return None
        if self.pair_label == "fist":
            return "speaker_mute" if now - self.pair_since + TIME_EPSILON >= PAIR_HOLD_SECONDS else None
        start, first_x, second_x, first_y, second_y = self.pair_motion[0]
        _now, first, second, first_now_y, second_now_y = self.pair_motion[-1]
        first_dx, second_dx = first - first_x, second - second_x
        change = abs(second - first) - abs(second_x - first_x)
        if (
            0.15 <= now - start <= MOTION_WINDOW_SECONDS and first_dx * second_dx < 0
            and min(abs(first_dx), abs(second_dx)) >= 0.06 and abs(change) >= 0.15
            and max(abs(first_now_y - first_y), abs(second_now_y - second_y)) <= 0.12
        ):
            return "zoom_in" if change > 0 else "zoom_out"
        return None

    def _hand_action(self, state: HandState, other: HandState | None, now: float) -> str | None:
        if state.fired or state.since is None:
            return None
        held = now - state.since + TIME_EPSILON
        if state.label in REPEAT_ACTIONS:
            if held < REPEAT_START_SECONDS or now + TIME_EPSILON < state.next_repeat:
                return None
            state.next_repeat = self.cooldown = now + REPEAT_SECONDS
            return REPEAT_ACTIONS[state.label]
        action = None
        if state.label in HOLD_ACTIONS and held >= HOLD_SECONDS:
            action = HOLD_ACTIONS[state.label]
        elif state.label == "open" and state.motion:
            start, origin_x, origin_y = state.motion[0]
            _now, x, y = state.motion[-1]
            dx, dy = x - origin_x, y - origin_y
            # Hands moving apart or together belong to zoom, never to a one-hand swipe.
            other_dx = other.motion[-1][1] - other.motion[0][1] if other and other.motion else 0.0
            opposite = other_dx * dx < 0 and abs(other_dx) >= 0.06
            if 0.15 <= now - start <= MOTION_WINDOW_SECONDS and abs(dx) >= 0.22 and abs(dy) <= 0.12 and not opposite:
                action = "right" if dx > 0 else "left"
        if action:
            for candidate in self.hands.values():
                if candidate.label == state.label:
                    candidate.fired = True
                    candidate.fired_label = candidate.label
            self.cooldown = now + ACTION_COOLDOWN_SECONDS
        return action


def desktop_available() -> bool:
    if sys.platform != "win32":
        return False
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.OpenInputDesktop.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    user32.OpenInputDesktop.restype = wintypes.HANDLE
    user32.GetUserObjectInformationW.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
    user32.CloseDesktop.argtypes = [wintypes.HANDLE]
    handle = user32.OpenInputDesktop(0, False, 1)
    if not handle:
        return False
    try:
        name = ctypes.create_unicode_buffer(256)
        needed = wintypes.DWORD()
        return bool(user32.GetUserObjectInformationW(handle, 2, name, ctypes.sizeof(name), ctypes.byref(needed))) and name.value == "Default"
    finally:
        user32.CloseDesktop(handle)


def microphone_operation(device_id: str | None = None, muted: bool | None = None):
    try:
        import comtypes
        from pycaw.pycaw import AudioUtilities
        from pycaw.constants import DEVICE_STATE, EDataFlow, ERole
    except ImportError as exc:
        raise CameraAssistantError("dependency") from exc
    try:
        comtypes.CoInitialize()
    except (OSError, comtypes.COMError) as exc:
        raise CameraAssistantError("microphone") from exc
    try:
        devices = AudioUtilities.GetAllDevices(EDataFlow.eCapture.value, DEVICE_STATE.ACTIVE.value)
        if device_id is None:
            return [{"id": device.id, "name": device.FriendlyName} for device in devices]
        if device_id == "communications":
            endpoint = AudioUtilities.GetDeviceEnumerator().GetDefaultAudioEndpoint(
                EDataFlow.eCapture.value, ERole.eCommunications.value
            )
            device_id = endpoint.GetId()
        selected = next((device for device in devices if device.id == device_id), None)
        if selected is None or muted is None:
            raise CameraAssistantError("microphone")
        volume = selected.EndpointVolume
        volume.SetMute(int(muted), None)
        if bool(volume.GetMute()) != muted:
            raise CameraAssistantError("microphone")
        return selected.id
    except (OSError, comtypes.COMError) as exc:
        raise CameraAssistantError("microphone") from exc
    finally:
        comtypes.CoUninitialize()


def perform_action(action: str, settings: Settings) -> str | None:
    if not desktop_available():
        raise CameraAssistantError("locked", 409)
    if action == "mute":
        return microphone_operation(settings.microphone, True)
    if action not in {"left", "right"} and (action not in EXTRA_KEYS or not settings.extra_gestures):
        raise CameraAssistantError("settings", 400)
    try:
        import pyautogui
    except ImportError as exc:
        raise CameraAssistantError("dependency") from exc
    try:
        # Skip pyautogui's global 100 ms pause; the camera loop holds its lock while acting.
        if action in EXTRA_KEYS:
            keys = EXTRA_KEYS[action]
            if len(keys) == 1:
                pyautogui.press(keys[0], _pause=False)
            else:
                pyautogui.hotkey(*keys, _pause=False)
        elif settings.swipe_action == "media":
            pyautogui.press("nexttrack" if action == "right" else "prevtrack", _pause=False)
        else:
            pyautogui.hotkey("ctrl", "win", action, _pause=False)
    except (OSError, pyautogui.PyAutoGUIException) as exc:
        raise CameraAssistantError("action") from exc
    return None


class DetectionStopped(Exception):
    pass


class LandmarkDetector:
    def __init__(self, settings: Settings, stop: threading.Event | None = None):
        try:
            import mediapipe as mp
        except (ImportError, OSError) as exc:
            raise CameraAssistantError("dependency") from exc
        self.mp = mp
        self.resources = ExitStack()
        try:
            if stop is not None and stop.is_set():
                raise DetectionStopped()
            vision = mp.tasks.vision
            self.pose = self.resources.enter_context(vision.PoseLandmarker.create_from_options(
                vision.PoseLandmarkerOptions(
                    base_options=mp.tasks.BaseOptions(model_asset_path=str(ensure_model("pose"))),
                    running_mode=vision.RunningMode.VIDEO,
                    min_pose_detection_confidence=0.7, min_pose_presence_confidence=0.7,
                )
            )) if settings.posture else None
            if stop is not None and stop.is_set():
                raise DetectionStopped()
            self.hand = self.resources.enter_context(vision.GestureRecognizer.create_from_options(
                vision.GestureRecognizerOptions(
                    base_options=mp.tasks.BaseOptions(model_asset_path=str(ensure_model("gesture"))),
                    running_mode=vision.RunningMode.VIDEO, num_hands=2,
                    min_hand_detection_confidence=0.5, min_hand_presence_confidence=0.5,
                )
            )) if settings.gestures else None
            if stop is not None and stop.is_set():
                raise DetectionStopped()
            self.source = CameraSource.acquire(settings.camera_index)
            self.resources.callback(self.source.close)
        except (DetectionStopped, PresenceError, CameraAssistantError, OSError, RuntimeError, ValueError):
            self.resources.close()
            raise
        self.timestamp = 0
        self.next_pose = 0.0
        self.body: list[Point] = []

    def read(self) -> tuple[list[Point], list[tuple[str, list[Point], str, float]]]:
        cv2 = self.source.cv2
        try:
            frame = cv2.cvtColor(cv2.flip(self.source.read(), 1), cv2.COLOR_BGR2RGB)
            image = self.mp.Image(image_format=self.mp.ImageFormat.SRGB, data=frame)
            now = time.monotonic()
            self.timestamp = max(self.timestamp + 1, int(now * 1000))
            result = self.hand.recognize_for_video(image, self.timestamp) if self.hand else None
            if self.pose and now >= self.next_pose:
                pose = self.pose.detect_for_video(image, self.timestamp)
                self.body = [
                    Point(p.x, p.y, p.z, p.visibility or 0)
                    for p in pose.pose_landmarks[0]
                ] if pose.pose_landmarks else []
                self.next_pose = now + POSTURE_FRAME_SECONDS
            hands = []
            for index, landmarks in enumerate(result.hand_landmarks[:2] if result else []):
                categories = result.handedness[index] if index < len(result.handedness) else []
                side = categories[0].category_name if categories else ""
                gestures = result.gestures[index] if index < len(result.gestures) else []
                category = (gestures[0].category_name or "") if gestures else ""
                confidence = gestures[0].score if gestures else 0.0
                points = [Point(p.x, p.y, p.z) for p in landmarks]
                if len(points) == 21:
                    hands.append((side if side in {"Left", "Right"} else "", points, category, confidence))
            hands.sort(key=lambda item: item[1][0].x)
            # The frame is mirrored, so labels match the user's real hands; resolve doubles by position.
            if len(hands) == 2 and {hand[0] for hand in hands} != {"Left", "Right"}:
                hands = [("Left", *hands[0][1:]), ("Right", *hands[1][1:])]
            elif len(hands) == 1 and not hands[0][0]:
                hands = [("Hand", *hands[0][1:])]
            return self.body, hands
        except (cv2.error, RuntimeError, ValueError) as exc:
            raise CameraAssistantError("vision") from exc

    def close(self) -> None:
        self.resources.close()


class CameraAssistantMonitor:
    def __init__(self, on_reminder: Callable[[], None] | None = None):
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._settings = Settings()
        self._posture = PostureTracker(30)
        self._gestures = GestureTracker()
        self._training: Calibration | None = None
        self._phase = "stopped"
        self._error = ""
        self._error_nl = ""
        self._notice = ""
        self._alerts = 0
        self._actions = 0
        self._last_action = ""
        self._muted_device: str | None = None
        self._points = {"pose": [], "hand": []}
        self._on_reminder = on_reminder
        self._frame_times: deque[float] = deque(maxlen=20)
        self._processing_ms = 0.0

    def snapshot(self, dutch: bool = False) -> dict:
        with self._lock:
            span = self._frame_times[-1] - self._frame_times[0] if len(self._frame_times) > 1 else 0
            return {
                "running": bool(self._thread and self._thread.is_alive()),
                "phase": self._phase, "settings": asdict(self._settings),
                "error_message": self._error_nl if dutch else self._error, "notice": self._notice,
                "posture_state": self._posture.phase,
                "posture_calibrated": self._posture.baseline is not None,
                "trained": sorted(self._gestures.examples),
                "gesture_ready": self._gestures.ready,
                "gesture": self._gestures.label, "armed": self._gestures.armed,
                "hands": self._gestures.hand_labels(),
                "cooldown_seconds": round(max(0.0, self._gestures.cooldown - self._gestures.last), 1),
                "training": self._training.target if self._training else "",
                "progress": self._training.progress if self._training else 0,
                "alerts": self._alerts, "actions": self._actions,
                "last_action": self._last_action,
                "muted_by_echo": self._muted_device is not None,
                "points": self._points,
                "fps": round((len(self._frame_times) - 1) / span, 1) if span > 0 else 0,
                "processing_ms": self._processing_ms,
            }

    def start(self, settings: Settings) -> None:
        if sys.platform != "win32":
            raise PresenceError("unsupported")
        with self._lock:
            if self._thread and self._thread.is_alive():
                raise CameraAssistantError("running", 409)
            self._settings = settings
            self._posture = PostureTracker(settings.delay_seconds)
            self._gestures = GestureTracker(settings.extra_gestures)
            self._training = None
            self._alerts = self._actions = 0
            self._last_action = self._error = self._error_nl = self._notice = ""
            self._phase = "starting"
            self._frame_times.clear()
            self._processing_ms = 0.0
            self._stop.clear()
            self._thread = threading.Thread(target=self._run, name="echo-camera-assistant", daemon=True)
            self._thread.start()

    def stop(self) -> None:
        with self._lock:
            self._stop.set()
            self._gestures.armed = False
            worker = self._thread
            if worker and worker.is_alive() and not self._error:
                self._phase = "stopping"
        if worker:
            worker.join(timeout=3)

    def train(self, target: str) -> None:
        with self._lock:
            if self._phase != "monitoring":
                raise CameraAssistantError("inactive", 409)
            if target not in {"posture", "open", "fist", "activate"}:
                raise CameraAssistantError("settings", 400)
            if not (self._settings.posture if target == "posture" else self._settings.gestures):
                raise CameraAssistantError("settings", 400)
            self._gestures.armed = False
            self._gestures.reset_motion()
            self._training = Calibration(target, time.monotonic())
            self._notice = ""

    def arm(self, enabled: bool) -> None:
        with self._lock:
            if type(enabled) is not bool:
                raise CameraAssistantError("settings", 400)
            if enabled and (self._phase != "monitoring" or self._training or not self._gestures.ready):
                raise CameraAssistantError("training", 409)
            cancelled_scan = not enabled and self._training is not None and self._training.target == "activate"
            if cancelled_scan:
                self._training = None
            self._gestures.reset_motion()
            self._gestures.armed = enabled
            self._notice = "scan_cancelled" if cancelled_scan else ""

    def unmute(self) -> None:
        with self._lock:
            if not desktop_available():
                raise CameraAssistantError("locked", 409)
            if self._muted_device is None:
                raise CameraAssistantError("microphone", 409)
            microphone_operation(self._muted_device, False)
            self._muted_device = None

    def _observe(self, body: list[Point], hands: list[tuple[str, list[Point], str, float]], now: float) -> None:
        hands = sorted(hands, key=lambda hand: hand[1][0].x if hand[1] else 0.5)
        self._points = {
            "pose": [[round(p.x, 3), round(p.y, 3)] for p in body],
            "hand": [[round(p.x, 3), round(p.y, 3)] for _side, points, _category, _score in hands for p in points],
        }
        observations = [HandObservation.from_points(*hand) for hand in hands]
        posture = posture_features(body)
        # Calibration needs one unambiguous hand; the learned shapes then apply to both hands.
        fingers = observations[0].values if len(observations) == 1 else None
        if self._training:
            self._posture.since = None
            training = self._training
            if now >= training.deadline:
                self._training = None
                self._notice = "training_failed"
                return
            if training.target == "activate":
                values = (1.0,) if len(observations) == 1 and self._gestures.classify(observations[0]) == "open" else None
            else:
                values = posture if training.target == "posture" else fingers
            result = training.observe(values, now)
            if result is not None:
                if training.target == "activate":
                    self._gestures.scanned = True
                    self._gestures.reset_motion()
                    self._gestures.armed = True
                    self._notice = "scan_complete"
                elif training.target == "posture":
                    self._posture.baseline = result
                    self._posture.since = None
                else:
                    other = self._gestures.examples.get("fist" if training.target == "open" else "open")
                    if other is not None and sum(abs(a - b) >= 0.35 for a, b in zip(result, other)) < 3:
                        self._training = None
                        self._notice = "training_failed"
                        return
                    self._gestures.examples[training.target] = result
                self._training = None
                if training.target != "activate":
                    self._notice = "trained"
            return
        if self._settings.posture and self._posture.observe(posture, now):
            self._alerts += 1
            self._notice = "posture_reminder"
            if self._on_reminder:
                self._on_reminder()
            if self._settings.sound:
                import winsound
                winsound.MessageBeep(winsound.MB_OK)
        if self._settings.gestures:
            action = self._gestures.observe(observations, now)
            if action:
                try:
                    muted_device = perform_action(action, self._settings)
                except CameraAssistantError as exc:
                    LOGGER.exception("Gesture action failed")
                    self._gestures.armed = False
                    self._notice = exc.code
                else:
                    self._actions += 1
                    self._last_action = action
                    if muted_device:
                        self._muted_device = muted_device

    def _run(self) -> None:
        detector = None
        try:
            detector = LandmarkDetector(self._settings, self._stop)
            while not self._stop.is_set():
                started = time.monotonic()
                body, hands = detector.read()
                with self._lock:
                    if self._stop.is_set():
                        break
                    if not desktop_available():
                        self._phase = "paused"
                        self._gestures.armed = False
                        self._gestures.reset_motion()
                        self._posture.since = None
                        self._training = None
                        if self._notice == "scan_complete":
                            self._notice = ""
                        self._points = {"pose": [], "hand": []}
                        self._frame_times.clear()
                        self._processing_ms = 0.0
                    else:
                        self._phase = "monitoring"
                        self._observe(body, hands, time.monotonic())
                        self._frame_times.append(time.monotonic())
                        self._processing_ms = round((time.monotonic() - started) * 1000, 1)
                period = GESTURE_FRAME_SECONDS if self._settings.gestures else POSTURE_FRAME_SECONDS
                self._stop.wait(max(0, period - (time.monotonic() - started)))
        except DetectionStopped:
            self._stop.set()
        except (PresenceError, CameraAssistantError, OSError, RuntimeError, ValueError) as exc:
            LOGGER.exception("Camera assistant stopped")
            with self._lock:
                self._error = str(exc)
                self._error_nl = exc.localized(True) if isinstance(exc, (PresenceError, CameraAssistantError)) else "De camera-assistent is gestopt door een verwerkingsfout. Controleer het Echo-logboek."
                self._phase = "error"
        finally:
            try:
                if detector:
                    detector.close()
            except (PresenceError, RuntimeError) as exc:
                LOGGER.exception("Camera assistant cleanup failed")
                with self._lock:
                    self._error = str(exc)
                    self._error_nl = "De camera kon niet goed worden vrijgegeven. Herstart Echo."
                    self._phase = "error"
            with self._lock:
                self._gestures.armed = False
                self._training = None
                self._points = {"pose": [], "hand": []}
                self._frame_times.clear()
                self._processing_ms = 0.0
                if not self._error:
                    self._phase = "stopped"
