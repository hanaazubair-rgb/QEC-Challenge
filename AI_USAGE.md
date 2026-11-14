# AI Usage – SignalSpeak (QEC 2026)

Per QEC rules, all use of generative AI is disclosed here. All AI-generated
code was reviewed, run, and tested by our team, and we can explain every part.

## Tools used
- **Claude Code (Anthropic)** – VS Code extension, used to write and edit code.
- **Claude (Anthropic) chat** – used for environment setup help, Git help,
  planning how to split the work, and reviewing code.

## What AI was used for

| File | What Claude did | What we did |
|------|-----------------|-------------|
| scanner.py + tests/test_scanner.py | Wrote scanning logic and tests from our spec; later added set_options() for switching screens | Designed the behaviour (step time, select, undo, slow_down), reviewed, tested |
| board.py | Wrote pygame UI from our spec; later added text shrink-to-fit, the hold progress bar and the red HELP banner | Chose layout, options, high contrast, no mouse/keyboard |
| speech.py | First version: pyttsx3 wrapper with one worker thread and a queue. Later rewritten to speak each phrase in its own short-lived process (the engine went silent after the first phrase on Windows) | Found the Windows bug, reviewed, tested on Windows |
| demo_board.py | Wrote test harness with fake selects | Used it to test UI before gestures were ready |
| flow.py + tests/test_flow.py | Wrote confirm step (“Send WATER? Confirm / Cancel”) and Pain 1–10 sub-menu from our spec | Designed the confirm/cancel flow and pain scale, reviewed |
| gestures.py + tests | Helped write detector (hysteresis + hold time), added last_strength, calibration ValueError, ease(), progress(), tests | Designed approach (personal baseline/peak), reviewed, tested |
| fatigue.py + tests/test_fatigue.py | Wrote FatigueMonitor and tests from our spec | Chose thresholds (25% strength drop, 50% longer gaps, window of 5), reviewed |
| tracker.py | Added automatic model download with an absolute path | Reviewed |
| emergency.py + tests/test_emergency.py | Wrote JawGestures and EmergencyAlert. Suggested splitting jawOpen into short hold = undo, 2 s hold = alert, so the two don't conflict | Chose the gesture and behaviour (2 s hold, “I need help now”, banner, undo to clear), tested |
| main.py | Wired in the progress bar and emergency alert (handle_jaw) | (teammate: fill in what you wrote vs. Claude) |
| calibration.py / saved profiles | (teammate: fill in) | |

## Example prompts
- "Write scanner.py – class Scanner(options, step_s=1.5) that highlights one
  option at a time... no pygame in here, so it's testable with fake times."
- "Write fatigue.py: a FatigueMonitor class... True if the average of the last
  5 strengths is 25%+ below the average of the first 5..."
- "While a gesture is being held, draw a progress bar filling across the
  highlighted box..."
- "Add an emergency alert: holding the mouth open (jawOpen) for 2 seconds,
  from ANY screen, immediately speaks 'I need help now' twice..."

## Not AI-generated
- The presentation and slides were made entirely by our team without AI.
- Product decisions (what the user needs, which gestures, confirm/cancel
  flow, fatigue adaptation, emergency alert) were made by our team.

## Third-party libraries (see README for full citations)
MediaPipe Face Landmarker [6] (library and face_landmarker.task model),
OpenCV, pygame-ce, pyttsx3, pytest.
