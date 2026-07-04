

# simple script to detect hand gestures and announce them via speech
# the original author used mediapipe.solutions; newer releases removed that
# namespace so we provide compatibility logic below.  see the comments for
# instructions if the code still fails.

import os
import sys
import cv2
import urllib.request
import contextlib
from typing import Any

# Add script directory to path so ``from model import ...`` always works.
_this_dir = os.path.dirname(os.path.abspath(__file__))
if _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)

# project utilities
import landmark_utils as u  # noqa: E402
import pyttsx3  # noqa: E402

# import dependencies; fail early with helpful message if something is wrong

try:
    import mediapipe as mp
except ImportError as exc:
    # re-raise with extra context rather than hiding the real problem; the
    # installer often sees a protobuf/tensorflow import error here which is
    # what you need to fix.
    raise ImportError(
        "failed to import mediapipe; ensure the package is installed "
        "and that its dependencies (tensorflow, protobuf, etc.) are "
        "compatible. original error: {}".format(exc)
    ) from exc

# figure out which API we have available
_use_old_api = hasattr(mp, "solutions")

# declare names upfront so the type checker knows they exist
mp_drawing: Any = None  # type: ignore[assignment]
mp_drawing_styles: Any = None  # type: ignore[assignment]
mp_hands: Any = None  # type: ignore[assignment]
vision: Any = None  # type: ignore[assignment]
HandLandmarker: Any = None  # type: ignore[assignment]
HandLandmarkerOptions: Any = None  # type: ignore[assignment]
VisionRunningMode: Any = None  # type: ignore[assignment]
BaseOptions: Any = None  # type: ignore[assignment]
_landmarker: Any = None  # type: ignore[assignment]

if not _use_old_api:
    # 0.10.x and later expose only ``mediapipe.tasks``; we will use the new
    # hand_landmarker below.  if you would rather stick with the old API then
    # downgrade to a mediapipe release <=0.10.0 (and/or use Python <=3.10).
    from mediapipe.tasks.python import vision  # type: ignore[import]
    from mediapipe.tasks.python.vision.hand_landmarker import (  # type: ignore[import]
        HandLandmarker,
        HandLandmarkerOptions,
    )
    from mediapipe.tasks.python.vision.core import (  # type: ignore[import,attr-defined]
        VisionRunningMode,  # type: ignore[attr-defined]
    )
    from mediapipe.tasks.python.core import BaseOptions  # type: ignore[import]
    # download default model if necessary
    MODEL_URL = "https://storage.googleapis.com/mediapipe-assets/hand_landmarker.task"
    MODEL_PATH = os.path.join(_this_dir, "model", "hand_landmarker.task")
    if not os.path.exists(MODEL_PATH):
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        print("downloading hand landmarker model (~12 MB)...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

    _landmarker_options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=VisionRunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    _landmarker = HandLandmarker.create_from_options(_landmarker_options)
else:
    # old API helpers
    mp_drawing = mp.solutions.drawing_utils  # type: ignore[attr-defined]
    mp_drawing_styles = mp.solutions.drawing_styles  # type: ignore[attr-defined]
    mp_hands = mp.solutions.hands  # type: ignore[attr-defined]

# import project modules
try:
    from model import KeyPointClassifier
except ImportError:
    from Translator.model import KeyPointClassifier

# ===============================
# common setup
# ===============================

kpclf = KeyPointClassifier()
gestures = {0: "Open Hand", 1: "Thumb", 2: "OK", 3: "Peace", 4: "No Hand Detected"}
engine = pyttsx3.init()
engine.setProperty("rate", 150)
last_spoken = ""

# ===============================
# camera
# ===============================
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("cannot open camera; check permissions/drivers or try a different index")

# helper to convert the new API result back into a form expected by the
# existing landmark utilities; this is mostly a tiny wrapper around the
# normalized landmarks objects.
def _wrap_landmarks(normalized_list):
    class Wrapper:
        def __init__(self, lst):
            self.landmark = lst

    return Wrapper(normalized_list)


# select appropriate context manager depending on API availability
if _use_old_api:
    hands_ctx = mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )
else:
    hands_ctx = contextlib.nullcontext()

with hands_ctx as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        image.flags.writeable = False
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        gesture_index = 4
        if _use_old_api:
            assert hands is not None  # type: ignore[assert-type]
            results = hands.process(image_rgb)
            image.flags.writeable = True
            image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    landmark_list = u.calc_landmark_list(image, hand_landmarks)
                    keypoints = u.pre_process_landmark(landmark_list)
                    gesture_index = int(kpclf(keypoints))
                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style(),
                    )
        else:
            mp_image = vision.Image(image_format=vision.ImageFormat.SRGB, data=image_rgb)  # type: ignore[attr-defined]
            # timestamp in ms; ``cap.get`` may not be accurate but it's fine here
            results = _landmarker.detect_for_video(mp_image, int(cap.get(cv2.CAP_PROP_POS_MSEC)))
            image.flags.writeable = True
            image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
            if results and results.hand_landmarks:
                for landmarks in results.hand_landmarks:
                    wrapper = _wrap_landmarks(landmarks)
                    landmark_list = u.calc_landmark_list(image, wrapper)
                    keypoints = u.pre_process_landmark(landmark_list)
                    # ensure we use a plain int to index `gestures`
                    gesture_index = int(kpclf(keypoints))
                    # draw simple circles/lines since drawing_utils isn't available
                    h, w, _ = image.shape
                    pts = [(int(pt.x * w), int(pt.y * h)) for pt in landmarks]
                    for p in pts:
                        cv2.circle(image, p, 3, (0, 255, 0), -1)
                    for i in range(len(pts) - 1):
                        cv2.line(image, pts[i], pts[i + 1], (0, 255, 0), 2)

        # display and speak
        final = cv2.flip(image, 1)
        label = gestures[int(gesture_index)]
        cv2.putText(final, label, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Sign to Audio", final)

        if label != last_spoken:
            engine.say(label)
            engine.runAndWait()
            last_spoken = label

        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()


