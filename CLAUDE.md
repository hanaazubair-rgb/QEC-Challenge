# SignalSpeak – QEC 2026
Python app: webcam → MediaPipe Face Landmarker → hands-free needs board for a user with ALS.

## Rules (competition)
- NO keyboard/mouse/voice INPUT to operate the app (Q to quit for devs only).
- Every third-party library or copied example must have a citation comment at the top of the file,
  e.g. `# Uses MediaPipe Face Landmarker [6] https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker`
- Code written with AI help: add `# Written with help from Claude Code (Anthropic)` at top of file.
- Keep README "Sources & AI use" section updated.

## Code style
- Logic (gestures, calibration, fatigue) is pure Python with no cv2/mediapipe imports → unit-testable.
- Type hints, small functions, docstrings. Tests in tests/ with pytest.
- Shared types live in core/types.py — don't change them without telling teammate.
