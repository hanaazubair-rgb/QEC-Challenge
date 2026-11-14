# Saves and loads a user's calibration so they don't have to recalibrate
# every session. Plain JSON files in profiles/. Own design; generated with
# help from Claude (Anthropic) - see AI_USAGE.md. Uses Python's json/pathlib.
import json
from pathlib import Path

PROFILE_DIR = Path("profiles")


def profile_path(name: str) -> Path:
    """File for this user's profile (name is cleaned to be filename-safe)."""
    safe = "".join(c for c in name if c.isalnum() or c in "-_") or "default"
    return PROFILE_DIR / f"{safe}.json"


def save_profile(name: str, data: dict) -> Path:
    """Write the profile; returns the file path."""
    path = profile_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))
    return path


def load_profile(name: str) -> dict | None:
    """Read the profile, or None if missing, damaged or not usable."""
    try:
        data = json.loads(profile_path(name).read_text())
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    if not (_valid_range(data.get("select")) and _valid_range(data.get("undo"))):
        return None
    return data


def _valid_range(value) -> bool:
    """A usable calibration is [baseline, peak] with peak above baseline."""
    return (isinstance(value, list) and len(value) == 2
            and all(isinstance(v, (int, float)) for v in value)
            and value[1] > value[0])