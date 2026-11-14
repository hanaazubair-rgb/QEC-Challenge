# Webcam tracking for SignalSpeak.
# Uses Google MediaPipe Face Landmarker [6] (Tasks API, VIDEO mode).
# Structure adapted from the MediaPipe Face Landmarker guide [6].
# Generated with help from Claude (Anthropic) - see AI_USAGE.md.
import time
import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

MODEL_PATH = "face_landmarker.task"


class Tracker:
    """Reads the webcam and returns blendshape scores (0..1) per frame."""

    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)
        options = vision.FaceLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=vision.RunningMode.VIDEO,
            output_face_blendshapes=True,
            num_faces=1,
        )
        self.landmarker = vision.FaceLandmarker.create_from_options(options)
        self._start = time.time()

    def read(self):
        """Returns (frame, scores). scores is a dict, or None if no face."""
        ok, frame = self.cap.read()
        if not ok:
            return None, None
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        ts = int((time.time() - self._start) * 1000)
        result = self.landmarker.detect_for_video(image, ts)
        if not result.face_blendshapes:
            return frame, None
        scores = {c.category_name: c.score for c in result.face_blendshapes[0]}
        return frame, scores

    def close(self):
        self.cap.release()
        self.landmarker.close()


if __name__ == "__main__":
    # Dev check only: shows live values for the signals we may use.
    WATCH = ["browInnerUp", "jawOpen", "eyeBlinkLeft", "eyeBlinkRight",
             "eyeLookUpLeft", "eyeLookDownLeft", "eyeLookInLeft", "eyeLookOutLeft"]
    t = Tracker()
    while True:
        frame, scores = t.read()
        if frame is None:
            break
        if scores:
            print("  ".join(f"{k[:12]}={scores[k]:.2f}" for k in WATCH), end="\r")
        cv2.imshow("tracker (dev)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):  # dev-only quit key
            break
    t.close()
    cv2.destroyAllWindows()