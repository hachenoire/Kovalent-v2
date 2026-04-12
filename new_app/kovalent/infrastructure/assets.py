from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pygame as pg

from ..config import BUTTON_IMAGE_DIR, IMAGE_DIR, SOUND_DIR
from ..domain.models import MusicTrack, SoundEffect


class _NullSound:
    """Fallback object used when audio is unavailable.

    Pygame audio can legitimately fail on headless systems or CI. Returning a
    no-op sound object keeps the rest of the code simple and predictable.
    """

    def play(self, *_args, **_kwargs) -> None:
        return None


@dataclass(slots=True)
class AssetStore:
    image_cache: dict[tuple[str, tuple[int, int]], pg.Surface] = field(default_factory=dict)
    font_cache: dict[int, pg.font.Font] = field(default_factory=dict)
    sound_cache: dict[SoundEffect, pg.mixer.Sound | _NullSound] = field(default_factory=dict)
    current_music_track: MusicTrack | None = None
    audio_ready: bool = False
    _image_paths: dict[str, Path] = field(init=False, repr=False)
    _sound_paths: dict[SoundEffect, Path] = field(init=False, repr=False)
    _music_paths: dict[MusicTrack, Path] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.audio_ready = self._ensure_audio()
        self._image_paths = {
            "title": IMAGE_DIR / "title.png",
            "lock": IMAGE_DIR / "lock.png",
            "icon": IMAGE_DIR / "icon.png",
            "restart": BUTTON_IMAGE_DIR / "restart.png",
            "next": BUTTON_IMAGE_DIR / "next.png",
        }
        self._sound_paths = {
            SoundEffect.BUTTON: SOUND_DIR / "btn-sfx.wav",
            SoundEffect.LINK: SOUND_DIR / "link-sfx.wav",
            SoundEffect.ERROR: SOUND_DIR / "error-sfx.wav",
            SoundEffect.WIN: SOUND_DIR / "win-sfx.wav",
        }
        self._music_paths = {
            MusicTrack.MAIN: SOUND_DIR / "music.wav",
            MusicTrack.DOOM: SOUND_DIR / "doom_music.wav",
        }

    def _ensure_audio(self) -> bool:
        try:
            if not pg.mixer.get_init():
                pg.mixer.init()
        except pg.error:
            return False
        return True

    def font(self, pixel_size: int) -> pg.font.Font:
        pixel_size = max(12, pixel_size)
        if pixel_size not in self.font_cache:
            self.font_cache[pixel_size] = pg.font.SysFont("freesansbold", pixel_size)
        return self.font_cache[pixel_size]

    def image(self, key: str, size: tuple[int, int]) -> pg.Surface:
        size = (max(1, size[0]), max(1, size[1]))
        cache_key = (key, size)
        if cache_key not in self.image_cache:
            raw = pg.image.load(str(self._image_paths[key])).convert_alpha()
            self.image_cache[cache_key] = pg.transform.smoothscale(raw, size)
        return self.image_cache[cache_key]

    def icon(self) -> pg.Surface:
        return self.image("icon", (32, 32))

    def play_sound(self, effect: SoundEffect) -> None:
        if effect not in self.sound_cache:
            if self.audio_ready:
                try:
                    self.sound_cache[effect] = pg.mixer.Sound(str(self._sound_paths[effect]))
                except pg.error:
                    self.sound_cache[effect] = _NullSound()
            else:
                self.sound_cache[effect] = _NullSound()
        self.sound_cache[effect].play()

    def sync_music(self, track: MusicTrack | None, *, enabled: bool) -> None:
        if not self.audio_ready:
            return

        if not enabled or track is None:
            if pg.mixer.music.get_busy():
                pg.mixer.music.stop()
            self.current_music_track = None
            return

        if self.current_music_track is track and pg.mixer.music.get_busy():
            return

        try:
            pg.mixer.music.load(str(self._music_paths[track]))
            pg.mixer.music.play(-1)
            self.current_music_track = track
        except pg.error:
            self.current_music_track = None

    def shutdown(self) -> None:
        if self.audio_ready and pg.mixer.music.get_busy():
            pg.mixer.music.stop()
