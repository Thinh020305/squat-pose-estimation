import cv2


def draw_status(frame, reps: int, score: int) -> None:
    cv2.putText(
        frame,
        f"Reps: {reps} Score: {score}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2,
    )
