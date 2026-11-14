# Text-to-speech for SignalSpeak. Uses pyttsx3
# https://pypi.org/project/pyttsx3/ [library, cited in presentation].
# pyttsx3's engine goes silent after the first phrase on Windows when it is
# reused, so each phrase is spoken by a fresh short-lived process. A new
# phrase cuts off the previous one. Written with help from Claude
# (Anthropic) - see AI_USAGE.md.
import subprocess
import sys

_SAY = (
    "import sys, pyttsx3\n"
    "e = pyttsx3.init()\n"
    "e.setProperty('rate', 150)\n"
    "e.say(sys.argv[1])\n"
    "e.runAndWait()\n"
)

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