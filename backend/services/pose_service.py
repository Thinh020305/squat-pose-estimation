from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field

import cv2
import mediapipe as mp

from .angle_service import Point, angle, vertical_torso_angle
from backend.services.squat_counter_service import SquatCounter


mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


@dataclass(frozen=True)
class SquatFeatures:
    knee_angle: float
    torso_lean: float
    visibility: float
    side: str
    model_features: dict[str, float]


class PoseAnalyzer:
    def __init__(self) -> None:
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.6,
        )

    def process(self, rgb_frame):
        return self.pose.process(rgb_frame)

    def extract_squat_features(self, landmarks) -> SquatFeatures | None:
        left = self._side_features(landmarks, "LEFT")
        right = self._side_features(landmarks, "RIGHT")
        candidates = [item for item in (left, right) if item]
        if not candidates:
            return None
        model_features = self._model_features(landmarks)
        if len(candidates) == 1:
            item = candidates[0]
            return SquatFeatures(item.knee_angle, item.torso_lean, item.visibility, item.side, model_features)
        visibility = sum(item.visibility for item in candidates)
        return SquatFeatures(
            sum(item.knee_angle * item.visibility for item in candidates) / visibility,
            sum(item.torso_lean * item.visibility for item in candidates) / visibility,
            visibility / len(candidates),
            "BOTH",
            model_features,
        )

    def _side_features(self, landmarks, side: str) -> SquatFeatures | None:
        shoulder = self._point(landmarks, f"{side}_SHOULDER")
        hip = self._point(landmarks, f"{side}_HIP")
        knee = self._point(landmarks, f"{side}_KNEE")
        ankle = self._point(landmarks, f"{side}_ANKLE")
        visibility = min(shoulder.visibility, hip.visibility, knee.visibility, ankle.visibility)
        if visibility < 0.35:
            return None
        return SquatFeatures(angle(hip, knee, ankle), vertical_torso_angle(shoulder, hip), visibility, side, {})

    def _model_features(self, landmarks) -> dict[str, float]:
        ls, rs = self._point(landmarks, "LEFT_SHOULDER"), self._point(landmarks, "RIGHT_SHOULDER")
        lh, rh = self._point(landmarks, "LEFT_HIP"), self._point(landmarks, "RIGHT_HIP")
        lk, rk = self._point(landmarks, "LEFT_KNEE"), self._point(landmarks, "RIGHT_KNEE")
        la, ra = self._point(landmarks, "LEFT_ANKLE"), self._point(landmarks, "RIGHT_ANKLE")
        lf, rf = self._point(landmarks, "LEFT_FOOT_INDEX"), self._point(landmarks, "RIGHT_FOOT_INDEX")
        lka, rka = angle(lh, lk, la), angle(rh, rk, ra)
        lha, rha = angle(ls, lh, lk), angle(rs, rh, rk)
        mid_shoulder = Point((ls.x + rs.x) / 2, (ls.y + rs.y) / 2)
        mid_hip = Point((lh.x + rh.x) / 2, (lh.y + rh.y) / 2)
        lean = vertical_torso_angle(mid_shoulder, mid_hip)
        shoulder_width = abs(ls.x - rs.x) or 1.0
        hip_width = abs(lh.x - rh.x) or shoulder_width
        return {
            "left_knee_angle": lka,
            "right_knee_angle": rka,
            "left_hip_angle": lha,
            "right_hip_angle": rha,
            "left_ankle_angle": angle(lk, la, lf),
            "right_ankle_angle": angle(rk, ra, rf),
            "spine_angle": 180 - lean,
            "torso_lean": 90 + lean,
            "left_knee_lateral": abs(lk.x - la.x) / shoulder_width,
            "right_knee_lateral": abs(rk.x - ra.x) / shoulder_width,
            "symmetry_score": abs(lka - rka) + abs(lha - rha),
            "hip_depth": ((lk.y + rk.y) / 2 - mid_hip.y) / hip_width,
        }

    @staticmethod
    def _point(landmarks, name: str) -> Point:
        item = landmarks.landmark[getattr(mp_pose.PoseLandmark, name).value]
        return Point(item.x, item.y, item.visibility)

    def close(self) -> None:
        self.pose.close()


@dataclass
class LiveWorkout:
    analyzer: PoseAnalyzer = field(default_factory=PoseAnalyzer)
    counter: SquatCounter = field(default_factory=SquatCounter)
    camera: cv2.VideoCapture = field(default_factory=lambda: cv2.VideoCapture(0))
    session_id: int | None = None
    last_score: int = 0
    last_label: str = ""
    last_feedback: str = "San sang tap Squat."
    knee_value: float | None = None
    torso_value: float | None = None
    stopped: bool = False



def _draw_workout_feedback(frame, workout: LiveWorkout) -> None:
    feedback = workout.last_feedback or "Dang cho ket qua danh gia."
    cv2.putText(
        frame,
        f"Squat feedback: {feedback}",
        (20, 78),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.62,
        (0, 255, 255),
        2,
    )
class PoseService:
    def __init__(self) -> None:
        self._workouts: dict[int, LiveWorkout] = {}
        self._lock = threading.Lock()

    def start(self, user_id: int, session_id: int) -> LiveWorkout:
        self.stop(user_id)
        workout = LiveWorkout(session_id=session_id)
        if not workout.camera.isOpened():
            workout.analyzer.close()
            raise RuntimeError("Khong mo duoc webcam.")
        with self._lock:
            self._workouts[user_id] = workout
        return workout

    def get(self, user_id: int) -> LiveWorkout | None:
        return self._workouts.get(user_id)

    def frames(self, user_id: int):
        workout = self._workouts[user_id]
        while not workout.stopped:
            ok, frame = workout.camera.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)
            result = workout.analyzer.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if result.pose_landmarks:
                mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                features = workout.analyzer.extract_squat_features(result.pose_landmarks)
                if features:
                    workout.knee_value = self._smooth(workout.knee_value, features.knee_angle)
                    workout.torso_value = self._smooth(workout.torso_value, features.torso_lean)
                    rep = workout.counter.update(
                        workout.knee_value,
                        workout.torso_value,
                        time.time(),
                        features.model_features,
                    )
                    if rep:
                        workout.last_score = rep.evaluation.total_score
                        workout.last_label = rep.evaluation.label
                        workout.last_feedback = rep.evaluation.feedback[0] if rep.evaluation.feedback else "Da ghi nhan rep."
            cv2.putText(
                frame,
                f"Reps: {workout.counter.count} Score: {workout.last_score}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )
            _draw_workout_feedback(frame, workout)

            ok, encoded = cv2.imencode(".jpg", frame)
            if ok:
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + encoded.tobytes() + b"\r\n"

    def stop(self, user_id: int) -> LiveWorkout | None:
        with self._lock:
            workout = self._workouts.pop(user_id, None)
        if workout:
            workout.stopped = True
            workout.camera.release()
            workout.analyzer.close()
        return workout

    @staticmethod
    def _smooth(previous: float | None, value: float, alpha: float = 0.35) -> float:
        return value if previous is None else alpha * value + (1 - alpha) * previous


pose_service = PoseService()






