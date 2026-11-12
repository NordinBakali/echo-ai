import hashlib
import io
import threading
import time
from dataclasses import asdict, replace
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock

import cv2
import numpy as np
import pytest

import echo_camera_assistant as coach
import echo_presence as presence


def test_posture_alert_exact_delay_and_two_minute_cooldown(camera_observation):
    baseline = coach.posture_features(camera_observation()[0])
    leaning = coach.posture_features(camera_observation(lean=0.1)[0])
    tracker = coach.PostureTracker(10)
    assert not tracker.observe(leaning, 0)
    tracker.baseline = baseline
    alerts = [i / 10 for i in range(1401) if tracker.observe(leaning, i / 10)]
    assert alerts == [10, 130]
    assert not tracker.observe(baseline, 140.1)
    assert tracker.phase == "upright" and tracker.since is None


def test_posture_missing_points_and_frame_gaps_reset_the_timer(camera_observation):
    tracker = coach.PostureTracker(10)
    tracker.baseline = coach.posture_features(camera_observation()[0])
    leaning = coach.posture_features(camera_observation(lean=0.1)[0])
    for i in range(100):
        assert not tracker.observe(leaning, i / 10)
    assert not tracker.observe(None, 10)
    assert tracker.phase == "no_pose"
    for i in range(101, 201):
        assert not tracker.observe(leaning, i / 10)
    assert not tracker.observe(leaning, 50)
    assert tracker.since == 50


def test_low_visibility_or_invalid_geometry_is_not_a_posture_judgment(camera_observation):
    body, hands = camera_observation()
    hand = hands[0][1]
    body[11] = coach.Point(0.3, 0.5, visibility=0.1)
    assert coach.posture_features(body) is None
    assert coach.posture_features([]) is None
    hand[0] = coach.Point(float("nan"), 0.8)
    assert coach.hand_features(hand) is None
    assert coach.hand_features([]) is None


@pytest.mark.parametrize("target", ["posture", "open", "fist"])
def test_personal_calibration_requires_two_seconds_of_valid_samples(camera_observation, target):
    body, hands = camera_observation("fist" if target == "fist" else "open")
    values = coach.posture_features(body) if target == "posture" else coach.hand_features(hands[0][1])
    training = coach.Calibration(target, 0)
    for i in range(20):
        assert training.observe(values, i / 10) is None
    assert training.observe(values, 2) == pytest.approx(values)
    assert training.progress == 100


def test_wrong_pose_and_tracking_loss_cannot_complete_training(hand_points):
    closed = coach.hand_features(hand_points("fist"))
    opened = coach.hand_features(hand_points("open"))
    training = coach.Calibration("open", 0)
    for i in range(21):
        assert training.observe(closed, i / 10) is None
    for i in range(21, 40):
        assert training.observe(opened, i / 10) is None
    assert training.observe(None, 4) is None
    assert training.progress == 0
    assert training.observe(opened, 5) is None
    assert len(training.samples) == 1


def trained_gestures(hand_points, extra=True):
    tracker = coach.GestureTracker(extra)
    tracker.examples = {kind: coach.hand_features(hand_points(kind)) for kind in ("open", "fist")}
    return tracker


def seen(values, x=0.5, y=0.5, side="Right"):
    return [coach.HandObservation(side, values, x, y)]


def pose(hand_points, kind, side="Right", x=0.5):
    return coach.HandObservation.from_points(side, hand_points(kind, x))


def fired_actions(tracker, frames, start=0.0):
    results = []
    for i, hands in enumerate(frames):
        action = tracker.observe(hands, start + i / 20)
        if action:
            results.append((start + i / 20, action))
    return results


def test_fist_is_practice_only_until_armed_and_fires_once(hand_points):
    tracker = trained_gestures(hand_points)
    fist = tracker.examples["fist"]
    for i in range(20):
        assert tracker.observe(seen(fist), i / 10) is None
    assert tracker.label == "fist"
    tracker.reset_motion()
    tracker.armed = True
    for i in range(8):
        assert tracker.observe(seen(fist), 2 + i / 10) is None
    assert tracker.observe(seen(fist), 2.800001) == "mute"
    for i in range(29, 100):
        assert tracker.observe(seen(fist), i / 10) is None


@pytest.mark.parametrize(("start", "end", "expected"), [(0.3, 0.6, "right"), (0.7, 0.4, "left")])
def test_swipe_threshold_direction_refractory_period_and_hand_identity(hand_points, start, end, expected):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    opened = tracker.examples["open"]
    assert tracker.observe(seen(opened, start), 0) is None
    assert tracker.observe(seen(opened, end), 0.1) is None
    assert tracker.observe(seen(opened, end), 0.2) == expected
    assert tracker.observe(seen(opened, start), 0.3) is None
    tracker.observe([], 0.4)
    tracker.observe(seen(opened, start), 0.5)
    assert tracker.observe(seen(opened, end), 0.8) is None
    tracker.observe([], 2)
    tracker.observe(seen(opened, start), 2.1)
    assert tracker.observe(seen(opened, end, side="Left"), 2.4) is None


def test_vertical_motion_and_large_frame_gaps_do_not_swipe(hand_points):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    opened = tracker.examples["open"]
    tracker.observe(seen(opened, 0.3, 0.3), 0)
    assert tracker.observe(seen(opened, 0.7, 0.7), 0.3) is None
    assert tracker.observe(seen(opened, 0.3, 0.3), 2) is None


def test_swipe_after_holding_hand_still_has_no_timer_blind_spot(hand_points):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    opened = tracker.examples["open"]
    for i in range(24):
        assert tracker.observe(seen(opened, 0.25), i * 0.05) is None
    assert tracker.observe(seen(opened, 0.37), 1.2) is None
    assert tracker.observe(seen(opened, 0.52), 1.25) == "right"
    assert tracker.observe(seen(opened, 0.75), 1.3) is None


def test_fast_swipe_remains_tracked_when_the_hand_jumps_between_frames(hand_points):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    opened = tracker.examples["open"]
    assert tracker.observe(seen(opened, 0.25), 0.0) is None
    assert tracker.observe(seen(opened, 0.6), 0.05) is None
    assert tracker.observe(seen(opened, 0.6), 0.15) == "right"


def test_thumb_direction_requires_a_clear_vertical_thumb(hand_points):
    assert coach.thumb_direction(hand_points("thumb_up")) == "up"
    assert coach.thumb_direction(hand_points("thumb_down")) == "down"
    for kind in ("open", "fist", "point", "peace"):
        assert coach.thumb_direction(hand_points(kind)) == ""
    sideways = hand_points("thumb_up")
    sideways[4] = coach.Point(0.2, 0.55)
    assert coach.thumb_direction(sideways) == ""
    tiny = [coach.Point(0.5 + (p.x - 0.5) / 5, 0.8 + (p.y - 0.8) / 5) for p in hand_points("thumb_up")]
    assert coach.thumb_direction(tiny) == ""
    assert coach.thumb_direction([]) == ""


@pytest.mark.parametrize(("kind", "basic"), [
    ("open", "open"), ("fist", "fist"), ("point", "unknown"),
    ("peace", "unknown"), ("thumb_up", "fist"), ("thumb_down", "fist"),
])
def test_extra_shapes_derive_from_open_and_fist_training(hand_points, kind, basic):
    assert trained_gestures(hand_points).classify(pose(hand_points, kind)) == kind
    assert trained_gestures(hand_points, extra=False).classify(pose(hand_points, kind)) == basic


def test_ambiguous_or_indistinct_templates_are_not_guessed():
    tracker = coach.GestureTracker()
    tracker.examples = {"open": (1.5, 1.5, 1.5, 1.5), "fist": (1.0, 0.5, 0.5, 0.5)}
    assert tracker.classify(coach.HandObservation("Right", (1.25, 0.5, 0.5, 0.5), 0.5, 0.5)) == "unknown"
    assert tracker.classify(coach.HandObservation("Right", (1.1, 0.5, 0.5, 0.5), 0.5, 0.5)) == "fist"
    tracker.examples["fist"] = (1.3, 0.5, 0.5, 0.5)
    assert "point" not in tracker.templates()
    assert tracker.classify(coach.HandObservation("Right", (1.5, 0.5, 0.5, 0.5), 0.5, 0.5)) == "fist"


@pytest.mark.parametrize(("values", "expected"), [
    ((2.12, 1.8, 1.6, 1.7), "open"),
    ((0.8, 0.5, 0.4, 0.45), "fist"),
    ((2.12, 0.5, 0.4, 0.45), "point"),
    ((2.12, 1.8, 0.4, 0.45), "peace"),
    ((1.025, 0.5, 0.4, 0.45), "unknown"),
    ((3.4, 1.8, 1.6, 1.7), "unknown"),
])
def test_recognition_tolerates_proportional_variation_without_guessing(values, expected):
    tracker = coach.GestureTracker()
    tracker.examples = {"open": (1.7, 1.8, 1.6, 1.7), "fist": (0.35, 0.5, 0.4, 0.45)}
    assert tracker.classify(coach.HandObservation("Right", values, 0.5, 0.5)) == expected


def test_proportional_recognition_requires_distinct_calibration_and_enabled_extras():
    tracker = coach.GestureTracker(extra=False)
    tracker.examples = {"open": (1.7, 1.8, 1.6, 1.7), "fist": (0.35, 0.5, 0.4, 0.45)}
    assert tracker.classify(coach.HandObservation("Right", (2.12, 0.5, 0.4, 0.45), 0.5, 0.5)) == "unknown"
    tracker.examples["fist"] = (1.5, 0.5, 0.4, 0.45)
    assert tracker.classify(coach.HandObservation("Right", (2.12, 0.5, 0.4, 0.45), 0.5, 0.5)) == "unknown"


def test_brief_uncertain_frames_do_not_prevent_a_hold_or_repeat_it(hand_points):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    fist = pose(hand_points, "fist")
    uncertain = coach.HandObservation("Right", None, fist.x, fist.y)
    actions = []
    for i in range(100):
        hand = uncertain if i % 5 == 4 else fist
        action = tracker.observe([hand], i / 20)
        if hand is uncertain:
            assert action is None
        if action:
            actions.append((i / 20, action))
    assert len(actions) == 1
    assert 0.8 <= actions[0][0] <= 1.5
    assert actions[0][1] == "mute"


def test_uncertain_pose_cannot_rearm_a_one_shot_until_a_clear_release(hand_points):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    fist = pose(hand_points, "fist")
    uncertain = coach.HandObservation("Right", None, fist.x, fist.y)
    frames = [[fist]] * 21 + [[uncertain]] * 10 + [[fist]] * 70
    assert [action for _time, action in fired_actions(tracker, frames)] == ["mute"]
    opened = pose(hand_points, "open")
    assert [action for _time, action in fired_actions(tracker, [[opened]] * 5 + [[fist]] * 21, start=6)] == ["mute"]


def test_long_processing_gap_resets_hold_without_rearming_a_fired_gesture(hand_points):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    fist = pose(hand_points, "fist")
    assert [action for _time, action in fired_actions(tracker, [[fist]] * 21)] == ["mute"]
    assert fired_actions(tracker, [[fist]] * 80, start=3) == []


def test_one_misclassified_frame_cannot_rearm_a_completed_action(hand_points):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    fist = pose(hand_points, "fist")
    opened = pose(hand_points, "open")
    frames = [[fist]] * 21 + [[opened]] + [[fist]] * 80
    assert [action for _time, action in fired_actions(tracker, frames)] == ["mute"]


def test_moving_pointing_hand_does_not_toggle_music(hand_points):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    frames = [[pose(hand_points, "point", x=0.25 + i * 0.015)] for i in range(25)]
    assert fired_actions(tracker, frames) == []
    stationary = [[pose(hand_points, "point", x=0.61)]] * 20
    assert [action for _time, action in fired_actions(tracker, stationary, start=1.25)] == ["play_pause"]


@pytest.mark.parametrize("scale", [0.6, 1, 1.4])
def test_pinch_gap_is_normalized_to_palm_size(hand_points, scale):
    points = [coach.Point(0.5 + (p.x - 0.5) * scale, 0.5 + (p.y - 0.5) * scale, p.z * scale)
              for p in hand_points("pinch")]
    assert coach.pinch_gap(points) == pytest.approx(0.15)
    tracker = coach.GestureTracker(True)
    hand = coach.HandObservation.from_points("Right", points, "None", 0)
    assert tracker.classify(hand) == "pinch"
    assert tracker.classify(replace(hand, confidence=float("nan"))) == "unknown"


@pytest.mark.parametrize("kind", ["open", "fist", "point", "peace", "thumb_up", "thumb_down"])
def test_regular_poses_are_not_pinches(hand_points, kind):
    gap = coach.pinch_gap(hand_points(kind))
    assert gap is None or gap > coach.PINCH_START_RATIO


@pytest.mark.parametrize("bad", ["missing", "invisible", "nonfinite", "outside", "tiny"])
def test_invalid_pinch_landmarks_cannot_control_volume(hand_points, bad):
    points = hand_points("pinch")
    if bad == "missing":
        points.pop()
    elif bad == "invisible":
        points[4] = replace(points[4], visibility=0.1)
    elif bad == "nonfinite":
        points[4] = replace(points[4], z=float("nan"))
    elif bad == "outside":
        points[8] = replace(points[8], x=1.1)
    else:
        points[9] = replace(points[0], y=0.79)
    assert coach.pinch_gap(points) is None


def test_pinch_volume_clutch_hysteresis_and_single_step_per_movement(hand_points):
    tracker = coach.GestureTracker(True)
    tracker.armed = True
    closed = pose(hand_points, "pinch")
    wide = pose(hand_points, "pinch_wide")
    assert tracker.classify(wide) != "pinch"
    assert tracker.classify(wide, pinching=True) == "pinch"
    assert fired_actions(tracker, [[closed]] * 12) == []
    frames = [[wide]] * 30 + [[closed]] * 30
    actions = fired_actions(tracker, frames, start=0.6)
    assert [action for _time, action in actions] == ["volume_up", "volume_down"]
    assert tracker.label == "pinch"


def test_brief_pinch_and_jitter_do_not_change_volume(hand_points):
    tracker = coach.GestureTracker(True)
    tracker.armed = True
    closed = pose(hand_points, "pinch")
    wide = pose(hand_points, "pinch_wide")
    assert fired_actions(tracker, [[closed]] * 3 + [[wide]] * 40) == []
    tracker.reset_motion()
    frames = [[replace(closed, pinch=0.15 + (i % 3 - 1) * 0.04)] for i in range(60)]
    assert fired_actions(tracker, frames, start=3) == []


@pytest.mark.parametrize(("extra", "armed"), [(True, False), (False, True)])
def test_pinch_requires_extra_gestures_and_explicit_activation(hand_points, extra, armed):
    tracker = coach.GestureTracker(extra)
    tracker.armed = armed
    frames = [[pose(hand_points, "pinch")]] * 20 + [[pose(hand_points, "pinch_wide")]] * 20
    assert fired_actions(tracker, frames) == []


@pytest.mark.parametrize("loss", ["absent", "uncertain", "overlap"])
def test_pinch_tracking_loss_discards_volume_baseline(hand_points, loss):
    tracker = coach.GestureTracker(True)
    tracker.armed = True
    closed = pose(hand_points, "pinch")
    wide = pose(hand_points, "pinch_wide")
    assert fired_actions(tracker, [[closed]] * 12) == []
    if loss == "absent":
        hands = []
    elif loss == "uncertain":
        hands = [replace(closed, pinch=None, values=None)]
    else:
        hands = [closed, replace(closed, identity="Left", x=closed.x + 0.01)]
    assert tracker.observe(hands, 0.6) is None
    assert fired_actions(tracker, [[wide]] * 20, start=0.65) == []
    actions = fired_actions(tracker, [[closed]] * 12, start=1.65)
    if loss == "overlap":
        assert actions == []
        assert [action for _time, action in fired_actions(tracker, [[wide]] * 12, start=2.25)] == ["volume_up"]
    else:
        assert [action for _time, action in actions] == ["volume_down"]


def test_pinch_suppresses_other_hand_and_conflicting_pinches(hand_points):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    closed = pose(hand_points, "pinch", x=0.25)
    wide = pose(hand_points, "pinch_wide", x=0.25)
    other = pose(hand_points, "fist", side="Left", x=0.75)
    assert fired_actions(tracker, [[closed, other]] * 20) == []
    actions = fired_actions(tracker, [[wide, other]] * 30, start=1)
    assert [action for _time, action in actions] == ["volume_up"]
    tracker.reset_motion()
    other = pose(hand_points, "pinch", side="Left", x=0.75)
    frames = [[closed, other]] * 20 + [[wide, other]] * 20
    assert fired_actions(tracker, frames, start=3) == []
    assert fired_actions(tracker, [[wide]] * 20, start=5) == []


def test_pinch_volume_steps_are_rate_limited(hand_points):
    tracker = coach.GestureTracker(True)
    tracker.armed = True
    closed = pose(hand_points, "pinch")
    assert fired_actions(tracker, [[closed]] * 12) == []
    frames = [[replace(closed, pinch=0.65 if i % 8 < 4 else 0.15)] for i in range(80)]
    actions = fired_actions(tracker, frames, start=0.6)
    assert {action for _time, action in actions} == {"volume_up", "volume_down"}
    assert all(b[0] - a[0] + coach.TIME_EPSILON >= coach.REPEAT_SECONDS for a, b in zip(actions, actions[1:]))


def test_pinch_can_lower_volume_without_first_raising_it(hand_points):
    tracker = coach.GestureTracker(True)
    tracker.armed = True
    assert fired_actions(tracker, [[pose(hand_points, "pinch")]] * 12) == []
    actions = fired_actions(tracker, [[pose(hand_points, "pinch_close")]] * 20, start=0.6)
    assert [action for _time, action in actions] == ["volume_down"]


def test_pinch_does_not_queue_another_hands_music_action(hand_points):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    closed = pose(hand_points, "pinch", x=0.25)
    other = pose(hand_points, "point", side="Left", x=0.75)
    assert fired_actions(tracker, [[closed, other]] * 40) == []
    assert fired_actions(tracker, [[other]] * 12, start=2) == []
    assert [action for _time, action in fired_actions(tracker, [[other]] * 12, start=2.6)] == ["play_pause"]


def test_pinch_preview_order_matches_hand_labels(camera_observation):
    monitor = coach.CameraAssistantMonitor()
    body, hands = camera_observation("point+pinch")
    monitor._observe(body, list(reversed(hands)), 0)
    snapshot = monitor.snapshot()
    assert snapshot["hands"] == [
        {"side": "Left", "gesture": "point", "needs_release": False},
        {"side": "Right", "gesture": "pinch", "needs_release": False},
    ]
    assert snapshot["points"]["hand"][0][0] == 0.35
    assert snapshot["points"]["hand"][21][0] == 0.65


def test_pinch_distance_change_from_camera_approach_is_not_volume(hand_points):
    tracker = coach.GestureTracker(True)
    tracker.armed = True
    frames = []
    for i in range(60):
        scale = 0.6 + i / 80
        points = [coach.Point(0.5 + (p.x - 0.5) * scale, 0.5 + (p.y - 0.5) * scale, p.z * scale)
                  for p in hand_points("pinch")]
        frames.append([coach.HandObservation.from_points("Right", points, "None", 0)])
    assert fired_actions(tracker, frames) == []


def test_large_hand_tracking_jump_does_not_repeat_a_completed_action(hand_points):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    fist = pose(hand_points, "fist", "Left", 0.2)
    moved = pose(hand_points, "fist", "Left", 0.9)
    opened = pose(hand_points, "open", "Right", 0.5)
    frames = [[fist, opened]] * 21 + [[moved, opened]] * 80
    assert [action for _time, action in fired_actions(tracker, frames)] == ["mute"]


def test_short_lost_hand_frame_preserves_hold_but_long_loss_resets_it(hand_points):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    fist = pose(hand_points, "fist")
    frames = [[fist]] * 8 + [[]] + [[fist]] * 28
    actions = fired_actions(tracker, frames)
    assert len(actions) == 1
    assert actions[0][1] == "mute" and actions[0][0] <= 1.05

    tracker = trained_gestures(hand_points)
    tracker.armed = True
    frames = [[fist]] * 8 + [[]] * 8 + [[fist]] * 8
    assert fired_actions(tracker, frames) == []


def test_handedness_label_flicker_does_not_restart_the_same_hand(hand_points):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    fist = coach.hand_features(hand_points("fist"))
    frames = [seen(fist, side="Left" if i % 2 else "Right") for i in range(40)]
    assert [action for _time, action in fired_actions(tracker, frames)] == ["mute"]


def test_two_hands_keep_their_tracks_when_handedness_labels_swap(hand_points):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    fist = coach.hand_features(hand_points("fist"))
    frames = [
        [coach.HandObservation("Right" if i % 2 else "Left", fist, 0.3, 0.5),
         coach.HandObservation("Left" if i % 2 else "Right", fist, 0.7, 0.5)]
        for i in range(60)
    ]
    assert [action for _time, action in fired_actions(tracker, frames)] == ["speaker_mute"]


def test_swapped_handedness_keeps_different_gestures_on_the_correct_hands(hand_points):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    fist = coach.hand_features(hand_points("fist"))
    opened = coach.hand_features(hand_points("open"))
    frames = [
        [coach.HandObservation("Right" if i % 2 else "Left", fist, 0.3, 0.5),
         coach.HandObservation("Left" if i % 2 else "Right", opened, 0.7, 0.5)]
        for i in range(50)
    ]
    assert [action for _time, action in fired_actions(tracker, frames)] == ["mute"]
    assert {item["side"]: item["gesture"] for item in tracker.hand_labels()} == {"Left": "fist", "Right": "open"}


def test_overlapping_hand_tracks_are_uncertain_and_never_fire(hand_points):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    fist = coach.hand_features(hand_points("fist"))
    hands = [coach.HandObservation("Left", fist, 0.495, 0.5),
             coach.HandObservation("Right", fist, 0.505, 0.5)]
    assert fired_actions(tracker, [hands] * 80) == []
    assert tracker.label == "unknown"


def test_flickering_two_fists_never_mute_microphone_or_repeat_speaker_action(hand_points):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    left = pose(hand_points, "fist", "Left", 0.3)
    right = pose(hand_points, "fist", "Right", 0.7)
    uncertain = coach.HandObservation("Right", None, right.x, right.y)
    frames = [[left, uncertain if i % 5 == 4 else right] for i in range(100)]
    assert [action for _time, action in fired_actions(tracker, frames)] == ["speaker_mute"]


def test_pair_can_repeat_after_one_hand_is_clearly_lowered(hand_points):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    left = pose(hand_points, "fist", "Left", 0.3)
    right = pose(hand_points, "fist", "Right", 0.7)
    frames = [[left, right]] * 25 + [[right]] * 50 + [[left, right]] * 30
    assert [action for _time, action in fired_actions(tracker, frames)] == ["speaker_mute", "speaker_mute"]


def test_leaving_a_two_fist_pose_requires_a_new_single_fist_hold(hand_points):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    left = pose(hand_points, "fist", "Left", 0.3)
    right = pose(hand_points, "fist", "Right", 0.7)
    frames = [[left, right]] * 10 + [[right]] * 18
    assert fired_actions(tracker, frames) == []


@pytest.mark.parametrize(("kind", "action"), [("fist", "mute"), ("point", "play_pause"), ("peace", "show_desktop")])
@pytest.mark.parametrize("side", ["Left", "Right"])
def test_hold_gestures_work_with_either_hand_while_the_other_hand_idles(hand_points, kind, action, side):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    other = "Right" if side == "Left" else "Left"
    hands = [pose(hand_points, kind, side, 0.3 if side == "Left" else 0.7),
             pose(hand_points, "open", other, 0.7 if side == "Left" else 0.3)]
    assert fired_actions(tracker, [hands] * 80) == [(pytest.approx(0.8), action)]
    assert {item["side"]: item["gesture"] for item in tracker.hand_labels()} == {side: kind, other: "open"}


def test_second_hand_entering_or_leaving_does_not_reset_the_first_hand(hand_points):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    fist = pose(hand_points, "fist", "Right", 0.7)
    other = pose(hand_points, "open", "Left", 0.3)
    frames = [[fist, other] if i % 4 < 2 else [fist] for i in range(16)]
    assert fired_actions(tracker, frames) == []
    assert tracker.observe([fist], 0.8) == "mute"


@pytest.mark.parametrize(("kind", "action"), [("thumb_up", "volume_up"), ("thumb_down", "volume_down")])
def test_thumbs_repeat_volume_steps_while_held(hand_points, kind, action):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    times = [moment for moment, name in fired_actions(tracker, [[pose(hand_points, kind)]] * 41) if name == action]
    assert times[0] == pytest.approx(0.6)
    assert len(times) >= 4
    assert all(0.3 - 1e-9 <= later - earlier <= 0.35 + 1e-9 for earlier, later in zip(times, times[1:]))


def test_two_fists_toggle_speaker_sound_instead_of_muting_the_microphone(hand_points):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    hands = [pose(hand_points, "fist", "Left", 0.3), pose(hand_points, "fist", "Right", 0.7)]
    assert fired_actions(tracker, [hands] * 100) == [(pytest.approx(1.0), "speaker_mute")]
    assert tracker.label == "two_fists"


@pytest.mark.parametrize(("start", "end", "action"), [((0.35, 0.65), (0.1, 0.9), "zoom_in"), ((0.1, 0.9), (0.35, 0.65), "zoom_out")])
def test_two_open_hands_zoom_once_and_never_swipe(hand_points, start, end, action):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    opened = tracker.examples["open"]
    frames = []
    for i in range(30):
        step = min(i / 12, 1)
        left, right = (a + (b - a) * step for a, b in zip(start, end))
        frames.append([coach.HandObservation("Left", opened, left, 0.5), coach.HandObservation("Right", opened, right, 0.5)])
    assert [name for _moment, name in fired_actions(tracker, frames)] == [action]
    assert tracker.label == "two_open"


def test_one_hand_can_swipe_while_the_other_open_hand_stays_still(hand_points):
    tracker = trained_gestures(hand_points)
    tracker.armed = True
    opened = tracker.examples["open"]
    frames = [[coach.HandObservation("Left", opened, 0.2, 0.5), coach.HandObservation("Right", opened, 0.5 + i * 0.05, 0.5)] for i in range(8)]
    assert [name for _moment, name in fired_actions(tracker, frames)] == ["right"]


def test_disabled_extra_gestures_keep_basic_controls_only(hand_points):
    tracker = trained_gestures(hand_points, extra=False)
    tracker.armed = True
    assert fired_actions(tracker, [[pose(hand_points, "point")]] * 40) == []
    two_fists = [pose(hand_points, "fist", "Left", 0.3), pose(hand_points, "fist", "Right", 0.7)]
    assert fired_actions(tracker, [two_fists] * 100, start=3) == [(pytest.approx(3.8), "mute")]
    opened = tracker.examples["open"]
    apart = [[coach.HandObservation("Left", opened, 0.35 - i * 0.03, 0.5), coach.HandObservation("Right", opened, 0.65 + i * 0.03, 0.5)] for i in range(12)]
    assert fired_actions(tracker, apart, start=10) == []


@pytest.mark.parametrize(("inference_seconds", "expected_period"), [(0.03, 0.05), (0.08, 0.08)])
def test_monitor_cadence_includes_processing_time(monkeypatch, camera_observation, inference_seconds, expected_period):
    clock = [0.0]
    starts = []
    monitor = coach.CameraAssistantMonitor()
    camera = Mock()

    def read():
        starts.append(clock[0])
        clock[0] += inference_seconds
        return camera_observation()

    camera.read.side_effect = read
    monitor._stop = Mock(spec=threading.Event)
    monitor._stop.is_set.side_effect = lambda: len(starts) >= 5
    monitor._stop.wait.side_effect = lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    monkeypatch.setattr(coach, "time", SimpleNamespace(monotonic=lambda: clock[0]))
    monkeypatch.setattr(coach, "LandmarkDetector", Mock(return_value=camera))
    monkeypatch.setattr(coach, "desktop_available", lambda: True)
    monitor._run()
    assert starts == pytest.approx([i * expected_period for i in range(5)])
    camera.close.assert_called_once()


def test_pose_sampling_leaves_capacity_for_hands_and_expires_missing_pose(monkeypatch, camera_observation):
    clock = [0.0]
    monkeypatch.setattr(coach, "time", SimpleNamespace(monotonic=lambda: clock[0]))
    detector = coach.LandmarkDetector.__new__(coach.LandmarkDetector)
    detector.source = Mock(cv2=cv2)
    detector.source.read.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
    detector.mp = SimpleNamespace(Image=lambda **_kwargs: object(), ImageFormat=SimpleNamespace(SRGB=1))
    detector.pose = Mock()
    detector.pose.detect_for_video.return_value = SimpleNamespace(pose_landmarks=[camera_observation()[0]])
    detector.hand = Mock()
    detector.hand.recognize_for_video.return_value = SimpleNamespace(hand_landmarks=[], handedness=[], gestures=[])
    detector.timestamp, detector.next_pose, detector.body = 0, 0.0, []
    for i in range(40):
        clock[0] = i / 20
        assert len(detector.read()[0]) == 33
    assert detector.hand.recognize_for_video.call_count == 40
    assert 8 <= detector.pose.detect_for_video.call_count <= 10
    detector.pose.detect_for_video.return_value = SimpleNamespace(pose_landmarks=[])
    clock[0] = 2.2
    assert detector.read() == ([], [])


def test_detector_returns_both_hands_sorted_with_unique_sides(hand_points):
    detector = coach.LandmarkDetector.__new__(coach.LandmarkDetector)
    detector.source = Mock(cv2=cv2)
    detector.source.read.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
    detector.mp = SimpleNamespace(Image=lambda **_kwargs: object(), ImageFormat=SimpleNamespace(SRGB=1))
    detector.pose = None
    detector.hand = Mock()
    detector.timestamp, detector.next_pose, detector.body = 0, 0.0, []

    def landmarks(kind, x):
        return [SimpleNamespace(x=p.x, y=p.y, z=p.z) for p in hand_points(kind, x)]

    def side(name):
        return [SimpleNamespace(category_name=name)] if name else []

    def detect(found, sides):
        categories = {"fist": "Closed_Fist", "open": "Open_Palm"}
        detector.hand.recognize_for_video.return_value = SimpleNamespace(
            hand_landmarks=[landmarks(kind, x) for kind, x in found],
            handedness=[side(name) for name in sides],
            gestures=[[SimpleNamespace(category_name=categories[kind], score=0.9)] for kind, _x in found],
        )
        hands = detector.read()[1]
        assert [(category, score) for _side, _points, category, score in hands] == [
            (categories[kind], 0.9) for kind, _x in sorted(found, key=lambda item: item[1])
        ]
        return [(name, points[0].x) for name, points, _category, _score in hands]

    assert detect([("fist", 0.7), ("open", 0.3)], ["Right", "Left"]) == [("Left", pytest.approx(0.3)), ("Right", pytest.approx(0.7))]
    assert detect([("fist", 0.7), ("open", 0.3)], ["Right", "Right"]) == [("Left", pytest.approx(0.3)), ("Right", pytest.approx(0.7))]
    assert detect([("fist", 0.7), ("open", 0.3)], ["Right", ""]) == [("Left", pytest.approx(0.3)), ("Right", pytest.approx(0.7))]
    assert detect([("open", 0.4)], ["Left"]) == [("Left", pytest.approx(0.4))]
    assert detect([("open", 0.4)], [""]) == [("Hand", pytest.approx(0.4))]
    assert detect([], []) == []
    detector.hand.recognize_for_video.return_value = SimpleNamespace(
        hand_landmarks=[landmarks("fist", 0.4)[:1]], handedness=[side("Left")],
        gestures=[[SimpleNamespace(category_name="Closed_Fist", score=0.99)]],
    )
    assert detector.read()[1] == []


def test_monitor_reports_actual_cadence_and_clears_it_after_stopping(monkeypatch, camera_observation):
    camera = Mock()
    camera.read.return_value = camera_observation()
    monkeypatch.setattr(coach, "LandmarkDetector", Mock(return_value=camera))
    monkeypatch.setattr(coach, "desktop_available", lambda: True)
    monitor = coach.CameraAssistantMonitor()
    try:
        monitor.start(coach.Settings())
        deadline = time.monotonic() + 3
        while camera.read.call_count < 8 and time.monotonic() < deadline:
            time.sleep(0.01)
        status = monitor.snapshot()
        assert camera.read.call_count >= 8
        assert 10 < status["fps"] <= 22
        assert status["processing_ms"] >= 0
    finally:
        monitor.stop()
    assert monitor.snapshot()["fps"] == 0
    assert monitor.snapshot()["processing_ms"] == 0


@pytest.mark.parametrize(("field", "value"), [
    ("camera_index", True), ("camera_index", -1), ("camera_index", 11),
    ("delay_seconds", 9), ("delay_seconds", 301), ("delay_seconds", "30"),
    ("posture", "yes"), ("gestures", 1), ("sound", None),
    ("swipe_action", "delete"), ("microphone", ""), ("microphone", 7), ("extra_gestures", "yes"),
])
def test_settings_strict_types_ranges_and_action_allowlist(field, value):
    data = asdict(coach.Settings())
    data[field] = value
    with pytest.raises(coach.CameraAssistantError) as error:
        coach.Settings.parse(data)
    assert error.value.status == 400


def test_missing_unknown_and_disabled_settings_are_rejected():
    for data in ({}, [], {**asdict(coach.Settings()), "unlock": True}, asdict(coach.Settings(posture=False, gestures=False))):
        with pytest.raises(coach.CameraAssistantError):
            coach.Settings.parse(data)


def test_model_download_integrity_cache_and_failed_download_cleanup(monkeypatch, tmp_path):
    expected = b"model fixture"
    monkeypatch.setattr(coach, "MODEL_DIR", tmp_path)
    monkeypatch.setitem(coach.MODELS, "gesture", ("gesture.task", "https://example.test/model", hashlib.sha256(expected).hexdigest()))
    fetch = Mock(return_value=io.BytesIO(expected))
    monkeypatch.setattr(coach.urllib.request, "urlopen", fetch)
    assert coach.ensure_model("gesture").read_bytes() == expected
    fetch.side_effect = AssertionError("Cache should work offline")
    assert coach.ensure_model("gesture").read_bytes() == expected
    (tmp_path / "gesture.task").write_bytes(b"corrupt")
    fetch.side_effect = None
    fetch.return_value = io.BytesIO(b"wrong model")
    with pytest.raises(coach.CameraAssistantError, match="verify"):
        coach.ensure_model("gesture")
    assert not list(tmp_path.glob("*.download"))
    assert (tmp_path / "gesture.task").read_bytes() == b"corrupt"


def test_presence_and_assistant_share_one_camera_until_both_stop(monkeypatch):
    capture = Mock()
    capture.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
    factory = Mock(return_value=capture)
    monkeypatch.setattr(cv2, "VideoCapture", factory)
    first = presence.CameraDetector(0)
    second = presence.CameraSource.acquire(0)
    try:
        assert first.read() is False
        assert second.read().shape == (480, 640, 3)
        first.close()
        capture.release.assert_not_called()
        assert second.read().size > 0
    finally:
        second.close()
    factory.assert_called_once()
    capture.release.assert_called_once()


@pytest.mark.parametrize(("mode", "action", "keys"), [
    ("media", "right", ("nexttrack",)), ("media", "left", ("prevtrack",)),
    ("desktop", "right", ("ctrl", "win", "right")), ("desktop", "left", ("ctrl", "win", "left")),
])
def test_exact_media_and_desktop_actions_without_real_keypresses(monkeypatch, mode, action, keys):
    import pyautogui
    monkeypatch.setattr(coach, "desktop_available", lambda: True)
    press, hotkey = Mock(), Mock()
    monkeypatch.setattr(pyautogui, "press", press)
    monkeypatch.setattr(pyautogui, "hotkey", hotkey)
    coach.perform_action(action, coach.Settings(swipe_action=mode))
    (press if mode == "media" else hotkey).assert_called_once_with(*keys, _pause=False)
    (hotkey if mode == "media" else press).assert_not_called()


@pytest.mark.parametrize(("action", "keys"), [
    ("play_pause", ("playpause",)), ("show_desktop", ("win", "d")),
    ("volume_up", ("volumeup",)), ("volume_down", ("volumedown",)), ("speaker_mute", ("volumemute",)),
    ("zoom_in", ("ctrl", "add")), ("zoom_out", ("ctrl", "subtract")),
])
def test_extra_actions_use_exact_windows_keys_and_respect_the_toggle(monkeypatch, action, keys):
    import pyautogui
    monkeypatch.setattr(coach, "desktop_available", lambda: True)
    press, hotkey = Mock(), Mock()
    monkeypatch.setattr(pyautogui, "press", press)
    monkeypatch.setattr(pyautogui, "hotkey", hotkey)
    assert all(pyautogui.isValidKey(key) and pyautogui.platformModule.keyboardMapping.get(key) for key in keys)
    coach.perform_action(action, coach.Settings())
    (press if len(keys) == 1 else hotkey).assert_called_once_with(*keys, _pause=False)
    with pytest.raises(coach.CameraAssistantError) as error:
        coach.perform_action(action, coach.Settings(extra_gestures=False))
    assert error.value.status == 400
    with pytest.raises(coach.CameraAssistantError):
        coach.perform_action("run_command", coach.Settings())
    assert press.call_count + hotkey.call_count == 1


def test_fist_mutes_selected_device_and_locked_desktop_blocks_actions(monkeypatch):
    operation = Mock(return_value="device-id")
    monkeypatch.setattr(coach, "microphone_operation", operation)
    monkeypatch.setattr(coach, "desktop_available", lambda: True)
    assert coach.perform_action("mute", coach.Settings(microphone="chosen")) == "device-id"
    operation.assert_called_once_with("chosen", True)
    monkeypatch.setattr(coach, "desktop_available", lambda: False)
    with pytest.raises(coach.CameraAssistantError, match="lock screen"):
        coach.perform_action("mute", coach.Settings())
    assert operation.call_count == 1


def test_native_microphone_api_is_capture_not_speaker_and_verifies_mute(monkeypatch):
    import comtypes
    from pycaw.pycaw import AudioUtilities
    from pycaw.constants import DEVICE_STATE, EDataFlow, ERole
    device = Mock(id="mic-id", FriendlyName="Test microphone")
    device.EndpointVolume.GetMute.return_value = 1
    devices = Mock(return_value=[device])
    enumerator = Mock()
    enumerator.GetDefaultAudioEndpoint.return_value.GetId.return_value = "mic-id"
    monkeypatch.setattr(AudioUtilities, "GetAllDevices", devices)
    monkeypatch.setattr(AudioUtilities, "GetDeviceEnumerator", lambda: enumerator)
    monkeypatch.setattr(comtypes, "CoInitialize", Mock())
    monkeypatch.setattr(comtypes, "CoUninitialize", Mock())
    assert coach.microphone_operation("communications", True) == "mic-id"
    devices.assert_called_once_with(EDataFlow.eCapture.value, DEVICE_STATE.ACTIVE.value)
    enumerator.GetDefaultAudioEndpoint.assert_called_once_with(EDataFlow.eCapture.value, ERole.eCommunications.value)
    device.EndpointVolume.SetMute.assert_called_once_with(1, None)
    with pytest.raises(coach.CameraAssistantError, match="microphone"):
        coach.microphone_operation("mic-id", False)


def test_monitor_stop_never_unmutes_and_explicit_restore_uses_exact_device(monkeypatch):
    monitor = coach.CameraAssistantMonitor()
    monitor._muted_device = "original-device"
    operation = Mock()
    monkeypatch.setattr(coach, "microphone_operation", operation)
    monkeypatch.setattr(coach, "desktop_available", lambda: True)
    monitor.stop()
    operation.assert_not_called()
    monitor.unmute()
    operation.assert_called_once_with("original-device", False)
    assert not monitor.snapshot()["muted_by_echo"]


def test_monitor_failure_is_explicit_localized_and_camera_is_released(monkeypatch):
    camera = Mock()
    camera.read.side_effect = presence.PresenceError("camera_read")
    monkeypatch.setattr(coach, "LandmarkDetector", Mock(return_value=camera))
    monitor = coach.CameraAssistantMonitor()
    monitor.start(coach.Settings())
    monitor._thread.join(timeout=3)
    assert monitor.snapshot()["phase"] == "error"
    assert "Geen camerabeelden" in monitor.snapshot(True)["error_message"]
    assert not monitor.snapshot()["running"]
    camera.close.assert_called_once()


def test_ambiguous_hand_calibration_is_rejected(monkeypatch, camera_observation):
    monitor = coach.CameraAssistantMonitor()
    monitor._gestures.examples["open"] = (1.2, 1.2, 1.2, 1.2)
    monitor._training = coach.Calibration("fist", 0)
    monkeypatch.setattr(monitor._training, "observe", lambda *_args: (1.0, 1.0, 1.0, 1.0))
    body, hands = camera_observation("fist")
    monitor._observe(body, hands, 2)
    assert monitor.snapshot()["notice"] == "training_failed"
    assert monitor.snapshot()["trained"] == ["open"]
    assert not monitor.snapshot()["armed"]


def test_training_needs_one_hand_but_both_hands_are_tracked_afterwards(camera_observation):
    monitor = coach.CameraAssistantMonitor()
    monitor._training = coach.Calibration("open", 0)
    body, hands = camera_observation("open+open")
    for i in range(30):
        monitor._observe(body, hands, i / 10)
    assert monitor._training.progress == 0 and not monitor._training.samples
    for target, start in (("open", 4), ("fist", 7)):
        monitor._training = coach.Calibration(target, start)
        body, hands = camera_observation(target)
        for i in range(21):
            monitor._observe(body, hands, start + i / 10)
    assert monitor.snapshot()["trained"] == ["fist", "open"]
    body, hands = camera_observation("point+fist")
    monitor._observe(body, hands, 10)
    status = monitor.snapshot()
    assert status["hands"] == [
        {"side": "Left", "gesture": "point", "needs_release": False},
        {"side": "Right", "gesture": "fist", "needs_release": False},
    ]
    assert status["gesture"] == "point"
    assert len(status["points"]["hand"]) == 42


def test_failed_action_disarms_but_does_not_claim_success(monkeypatch, camera_observation):
    monitor = coach.CameraAssistantMonitor()
    monitor._gestures.armed = True
    monkeypatch.setattr(monitor._gestures, "observe", lambda *_args: "mute")
    monkeypatch.setattr(coach, "perform_action", Mock(side_effect=coach.CameraAssistantError("microphone")))
    body, hands = camera_observation("fist")
    monitor._observe(body, hands, 1)
    status = monitor.snapshot()
    assert not status["armed"]
    assert status["actions"] == 0
    assert not status["muted_by_echo"]
    assert status["notice"] == "microphone"


def test_real_models_run_on_synthetic_pixels_without_camera_or_network(monkeypatch):
    if not all((coach.MODEL_DIR / data[0]).exists() for data in coach.MODELS.values()):
        pytest.skip("Optional model-runtime check requires previously downloaded model assets")
    camera = Mock(cv2=cv2)
    camera.read.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
    monkeypatch.setattr(coach.CameraSource, "acquire", Mock(return_value=camera))
    monkeypatch.setattr(coach.urllib.request, "urlopen", lambda *_args, **_kwargs: pytest.fail("No download expected"))
    detector = coach.LandmarkDetector(coach.Settings())
    try:
        assert detector.read() == ([], [])
    finally:
        detector.close()
    camera.close.assert_called_once()


def test_stopping_during_model_load_never_opens_camera(monkeypatch, tmp_path):
    import mediapipe as mp
    stopped = threading.Event()
    model = MagicMock()
    model.__enter__.return_value = model

    def load(_options):
        stopped.set()
        return model

    monkeypatch.setattr(coach, "ensure_model", lambda _kind: tmp_path / "model.task")
    monkeypatch.setattr(mp.tasks.vision.PoseLandmarker, "create_from_options", load)
    open_camera = Mock()
    monkeypatch.setattr(coach.CameraSource, "acquire", open_camera)
    with pytest.raises(coach.DetectionStopped):
        coach.LandmarkDetector(coach.Settings(), stopped)
    open_camera.assert_not_called()
    model.__exit__.assert_called_once()


def test_locked_desktop_disarms_and_never_acts(monkeypatch, camera_observation):
    camera = Mock()
    camera.read.return_value = camera_observation("fist")
    monkeypatch.setattr(coach, "LandmarkDetector", Mock(return_value=camera))
    monkeypatch.setattr(coach, "desktop_available", lambda: False)
    action = Mock()
    monkeypatch.setattr(coach, "perform_action", action)
    monitor = coach.CameraAssistantMonitor()
    try:
        monitor.start(coach.Settings())
        deadline = time.monotonic() + 3
        while monitor.snapshot()["phase"] == "starting" and time.monotonic() < deadline:
            time.sleep(0.01)
        assert monitor.snapshot()["phase"] == "paused"
        assert not monitor.snapshot()["armed"]
        action.assert_not_called()
    finally:
        monitor.stop()
    camera.close.assert_called_once()


@pytest.mark.parametrize(("category", "score", "extra", "expected"), [
    ("Open_Palm", 0.6, False, "open"),
    ("Closed_Fist", 0.9, False, "fist"),
    ("Pointing_Up", 0.9, True, "point"),
    ("Victory", 0.9, True, "peace"),
    ("Thumb_Up", 0.9, True, "thumb_up"),
    ("Thumb_Down", 0.9, True, "thumb_down"),
    ("Pointing_Up", 0.9, False, "unknown"),
    ("Thumb_Up", 0.9, False, "unknown"),
    ("Open_Palm", 0.599, True, "unknown"),
    ("Closed_Fist", float("nan"), True, "unknown"),
    ("None", 0.99, True, "unknown"),
    ("ILoveYou", 0.99, True, "unknown"),
])
def test_pretrained_categories_and_confidence_gate(category, score, extra, expected):
    tracker = coach.GestureTracker(extra)
    hand = coach.HandObservation("Right", None, 0.5, 0.5, category=category, confidence=score)
    assert tracker.classify(hand) == expected


def test_uncertain_model_result_never_falls_back_to_personal_template(hand_points):
    tracker = trained_gestures(hand_points)
    hand = coach.HandObservation(
        "Right", tracker.examples["fist"], 0.5, 0.5,
        category="Closed_Fist", confidence=0.1,
    )
    assert tracker.classify(hand) == "unknown"


@pytest.mark.parametrize(("values", "category", "score", "expected"), [
    ((1.25, 1.25, 1.25, 1.25), "None", 0.75, "open"),
    ((1.249, 1.36, 1.37, 1.35), "None", 0.75, "unknown"),
    ((1.36, 1.35, 1.35, 1.32), "None", 0.75, "open"),
    ((1.34, 1.36, 1.37, 1.35), "Open_Palm", 0.5, "open"),
    ((1.34, 1.36, 1.37, 1.35), "", 0.0, "open"),
    ((0.70, 0.69, 0.65, 0.75), "None", 0.75, "unknown"),
    ((1.33, 0.67, 0.63, 0.70), "None", 0.75, "unknown"),
    ((1.32, 1.37, 0.62, 0.65), "None", 0.75, "unknown"),
    ((1.34, 1.36, 1.37, 1.35), "Closed_Fist", 0.1, "unknown"),
    ((1.34, 1.36, 1.37, 1.35), "None", float("nan"), "unknown"),
])
def test_obvious_open_palm_geometry_handles_model_uncertainty(values, category, score, expected):
    hand = coach.HandObservation("Right", values, 0.5, 0.5, category=category, confidence=score)
    assert coach.GestureTracker().classify(hand) == expected


def test_one_scan_accepts_obvious_open_palm_when_model_returns_none(monkeypatch, camera_observation):
    monitor = coach.CameraAssistantMonitor()
    monitor._phase = "monitoring"
    monkeypatch.setattr(coach, "time", SimpleNamespace(monotonic=lambda: 0))
    monitor.train("activate")
    body, raw = camera_observation("open")
    hands = [(raw[0][0], raw[0][1], "None", 0.75)]
    for i in range(11):
        monitor._observe(body, hands, i / 10)
    assert monitor.snapshot()["armed"] and monitor.snapshot()["gesture_ready"]


def test_pretrained_two_hand_gesture_keeps_labels_after_tracking():
    tracker = coach.GestureTracker()
    tracker.armed = True
    hands = [
        coach.HandObservation("Left", None, 0.3, 0.5, category="Closed_Fist", confidence=0.9),
        coach.HandObservation("Right", None, 0.7, 0.5, category="Closed_Fist", confidence=0.9),
    ]
    assert fired_actions(tracker, [hands] * 40) == [(pytest.approx(1.0), "speaker_mute")]
    assert tracker.label == "two_fists"


def test_disabled_extra_model_gestures_never_trigger_basic_actions():
    tracker = coach.GestureTracker(extra=False)
    tracker.armed = True
    hand = coach.HandObservation("Right", None, 0.5, 0.5, category="Thumb_Up", confidence=0.95)
    assert fired_actions(tracker, [[hand]] * 60) == []
    fist = coach.HandObservation("Right", None, 0.5, 0.5, category="Closed_Fist", confidence=0.95)
    assert [action for _moment, action in fired_actions(tracker, [[fist]] * 40, start=4)] == ["mute"]


def test_one_open_hand_scan_arms_and_recognizes_fist_without_personal_templates(monkeypatch, camera_observation):
    monitor = coach.CameraAssistantMonitor()
    monitor._phase = "monitoring"
    monkeypatch.setattr(coach, "time", SimpleNamespace(monotonic=lambda: 0))
    action = Mock(return_value=None)
    monkeypatch.setattr(coach, "perform_action", action)
    body, raw_hands = camera_observation("open")
    opened = [(raw_hands[0][0], raw_hands[0][1], "Open_Palm", 0.95)]
    monitor._observe(body, opened, 0)
    assert not monitor.snapshot()["armed"]
    monitor.train("activate")
    for i in range(10):
        monitor._observe(body, opened, i / 10)
        assert not monitor.snapshot()["armed"]
    monitor._observe(body, opened, 1)
    status = monitor.snapshot()
    assert status["gesture_ready"] and status["armed"]
    assert status["notice"] == "scan_complete"
    assert not monitor._gestures.examples
    assert status["actions"] == 0
    body, raw_hands = camera_observation("fist")
    fist = [(raw_hands[0][0], raw_hands[0][1], "Closed_Fist", 0.95)]
    for i in range(12):
        monitor._observe(body, fist, 1.1 + i / 10)
    action.assert_called_once_with("mute", monitor._settings)


@pytest.mark.parametrize("reason", ["no_hand", "two_hands", "wrong_pose", "low_confidence"])
def test_one_scan_timeout_does_not_arm_on_ambiguous_frames(monkeypatch, camera_observation, reason):
    monitor = coach.CameraAssistantMonitor()
    monitor._phase = "monitoring"
    monkeypatch.setattr(coach, "time", SimpleNamespace(monotonic=lambda: 0))
    monitor.train("activate")
    body, raw = camera_observation("open")
    _, folded = camera_observation("fist")
    hand = (raw[0][0], raw[0][1], "Open_Palm", 0.95)
    cases = {
        "no_hand": [],
        "two_hands": [hand, ("Left", raw[0][1], "Open_Palm", 0.95)],
        "wrong_pose": [(raw[0][0], raw[0][1], "Closed_Fist", 0.95)],
        "low_confidence": [(folded[0][0], folded[0][1], "Open_Palm", 0.2)],
    }
    for i in range(151):
        monitor._observe(body, cases[reason], i / 10)
    status = monitor.snapshot()
    assert not status["gesture_ready"] and not status["armed"]
    assert status["notice"] == "training_failed"
    with pytest.raises(coach.CameraAssistantError):
        monitor.arm(True)


def test_scan_cannot_finish_after_deadline(monkeypatch, camera_observation):
    monitor = coach.CameraAssistantMonitor()
    monitor._phase = "monitoring"
    monkeypatch.setattr(coach, "time", SimpleNamespace(monotonic=lambda: 0))
    monitor.train("activate")
    body, raw = camera_observation("open")
    hand = [(raw[0][0], raw[0][1], "Open_Palm", 0.95)]
    for i in range(11):
        monitor._observe(body, hand, 14.1 + i / 10)
    assert not monitor.snapshot()["armed"]
    assert monitor.snapshot()["notice"] == "training_failed"


def test_practice_only_cancels_pending_scan_and_prevents_later_activation(monkeypatch, camera_observation):
    monitor = coach.CameraAssistantMonitor()
    monitor._phase = "monitoring"
    monkeypatch.setattr(coach, "time", SimpleNamespace(monotonic=lambda: 0))
    monitor.train("activate")
    body, hands = camera_observation("open")
    for i in range(6):
        monitor._observe(body, hands, i / 10)
    assert monitor.snapshot()["training"] == "activate"
    monitor.arm(False)
    assert monitor.snapshot()["notice"] == "scan_cancelled"
    assert not monitor.snapshot()["training"]
    for i in range(30):
        monitor._observe(body, hands, 0.6 + i / 10)
    assert not monitor.snapshot()["armed"]
    assert not monitor.snapshot()["gesture_ready"]
