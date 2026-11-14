# Written with help from Claude Code (Anthropic) - see AI_USAGE.md.
# Uses pyttsx3 text-to-speech https://pypi.org/project/pyttsx3/
# pyttsx3 is not thread-safe and can hang on Windows if runAndWait() is
# called from a new thread each time, so ONE worker thread owns the engine
# and reads phrases from a queue.

import queue
import threading

_queue: "queue.Queue[str]" = queue.Queue()
_worker: threading.Thread | None = None
_lock = threading.Lock()


def _run_worker() -> None:
    """Background loop: create the engine once, then speak queued text."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)   # a bit slower = clearer
    except Exception as err:              # no audio device / driver
        print(f"[speech] text-to-speech unavailable: {err}")
        engine = None
    while True:
        text = _queue.get()
        if engine is None:
            print(f"[speech] {text}")
            continue
        engine.say(text)
        engine.runAndWait()


def _ensure_worker() -> None:
    """Start the single worker thread the first time it is needed."""
    global _worker
    with _lock:
        if _worker is None:
            _worker = threading.Thread(target=_run_worker, daemon=True)
            _worker.start()


def speak(text: str) -> None:
    """Say text out loud without blocking the caller."""
    _ensure_worker()
    _queue.put(text)
