# Text-to-speech for SignalSpeak. Uses pyttsx3
# https://pypi.org/project/pyttsx3/ [library, cited in presentation].
# pyttsx3's engine goes silent after the first phrase on Windows when it is
# reused, so each phrase is spoken by a fresh short-lived process. A new
# phrase cuts off the previous one. Prefers a Canadian (then any female)
# voice if installed. Written with help from Claude (Anthropic) - see
# AI_USAGE.md.
import subprocess
import sys

_SAY = """
import sys, pyttsx3
# Earlier names win: Canadian first, then other female voices.
PREFERRED = ("canada", "linda", "zira", "hazel", "susan", "female")
e = pyttsx3.init()
e.setProperty("rate", 150)
voices = e.getProperty("voices")
chosen = None
for name in PREFERRED:
    for voice in voices:
        if name in voice.name.lower():
            chosen = voice
            break
    if chosen:
        break
if chosen:
    e.setProperty("voice", chosen.id)
e.say(sys.argv[1])
e.runAndWait()
"""

_process = None


def speak(text: str) -> None:
    """Say text out loud without blocking the caller."""
    global _process
    if _process is not None and _process.poll() is None:
        _process.terminate()              # cut off the previous phrase
    try:
        _process = subprocess.Popen([sys.executable, "-c", _SAY, text])
    except OSError as err:
        print(f"[speech] text-to-speech unavailable: {err}")
        print(f"[speech] {text}")