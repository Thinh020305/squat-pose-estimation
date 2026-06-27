import cv2


def encode_jpeg(frame) -> bytes | None:
    ok, encoded = cv2.imencode(".jpg", frame)
    return encoded.tobytes() if ok else None
