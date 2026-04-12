from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


# Keeping file system paths in one module avoids "magic relative paths" scattered
# across the codebase. This is especially useful when the project is launched
# from different working directories.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
NEW_APP_ROOT = PROJECT_ROOT / "new_app"
DATA_DIR = PROJECT_ROOT / "data"
IMAGE_DIR = DATA_DIR / "img"
BUTTON_IMAGE_DIR = IMAGE_DIR / "buttons"
SOUND_DIR = DATA_DIR / "sound"

ATOM_DATA_PATH = DATA_DIR / "atome.json"
LEVEL_DATA_PATH = DATA_DIR / "niveau.json"
LEGACY_PROGRESS_PATH = DATA_DIR / "progress.txt"
SAVE_DATA_PATH = NEW_APP_ROOT / "save_data.json"

BASE_WIDTH = 1200
BASE_HEIGHT = 800
FPS = 60
INTRO_DURATION_MS = 3200
STANDARD_LEVEL_COUNT = 50
SPEEDRUN_LAST_LEVEL = 40
SECRET_LEVEL = 51

# The gameplay coordinates stay expressed in this canonical space. The viewport
# later scales them to any actual window size, so gameplay code never has to
# care about pixels or monitor resolution.
PLAY_AREA = (60.0, 150.0, 1140.0, 740.0)


@dataclass(frozen=True, slots=True)
class AppConfig:
    window_title: str = "Kovalent Reforged"
    base_width: int = BASE_WIDTH
    base_height: int = BASE_HEIGHT
    fps: int = FPS
    intro_duration_ms: int = INTRO_DURATION_MS
    standard_level_count: int = STANDARD_LEVEL_COUNT
    speedrun_last_level: int = SPEEDRUN_LAST_LEVEL
    secret_level: int = SECRET_LEVEL
    play_area: tuple[float, float, float, float] = PLAY_AREA


CONFIG = AppConfig()
