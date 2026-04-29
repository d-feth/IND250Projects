"""
systems/audio_manager.py

Simple procedural audio manager for the game.

This module generates lightweight synthesized sound effects at runtime, so the
project does not depend on external sound asset files.

Sound categories:
- kickoff countdown beeps
- engine / acceleration hum
- boost pulse
- impacts
- goal sound

The system is intentionally simple and safe:
- if audio initialization fails, the game still runs
- repeated sounds use short cooldowns to avoid harsh spam
"""

from __future__ import annotations

import math
import random
import struct
import pygame

import config


class AudioManager:
    """
    Handles sound generation and playback for the project.
    """

    def __init__(self) -> None:
        self.audio_enabled = False

        self.sounds: dict[str, pygame.mixer.Sound] = {}

        # Dedicated looping/managed channels
        self.engine_channel: pygame.mixer.Channel | None = None
        self.boost_channel: pygame.mixer.Channel | None = None

        # Small cooldowns to prevent sound spam
        self.impact_cooldown_frames = 0

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(
                    frequency=config.AUDIO_FREQUENCY,
                    size=config.AUDIO_SIZE,
                    channels=config.AUDIO_CHANNELS,
                    buffer=config.AUDIO_BUFFER,
                )

            self.audio_enabled = True
            self._build_sounds()

            self.engine_channel = pygame.mixer.Channel(0)
            self.boost_channel = pygame.mixer.Channel(1)

        except pygame.error:
            # Fail gracefully. The game should still work with no audio.
            self.audio_enabled = False

    def _build_sounds(self) -> None:
        """
        Generate all reusable sounds.
        """
        self.sounds["countdown_beep"] = self._make_tone(
            frequency=660,
            duration=0.11,
            volume=config.COUNTDOWN_VOLUME,
            waveform="square",
            fade_out=True,
        )

        self.sounds["countdown_go"] = self._make_tone(
            frequency=920,
            duration=0.18,
            volume=config.COUNTDOWN_VOLUME,
            waveform="square",
            fade_out=True,
        )

        self.sounds["engine"] = self._make_tone(
            frequency=110,
            duration=0.18,
            volume=config.ENGINE_VOLUME,
            waveform="saw",
            fade_out=False,
        )

        self.sounds["boost"] = self._make_tone(
            frequency=180,
            duration=0.14,
            volume=config.BOOST_VOLUME,
            waveform="noise_tone",
            fade_out=False,
        )

        self.sounds["impact_soft"] = self._make_tone(
            frequency=190,
            duration=0.07,
            volume=config.IMPACT_VOLUME,
            waveform="click",
            fade_out=True,
        )

        self.sounds["impact_hard"] = self._make_tone(
            frequency=120,
            duration=0.10,
            volume=config.IMPACT_VOLUME,
            waveform="click",
            fade_out=True,
        )

        self.sounds["goal"] = self._make_goal_sound()

    def _make_tone(
        self,
        frequency: float,
        duration: float,
        volume: float,
        waveform: str = "sine",
        fade_out: bool = True,
    ) -> pygame.mixer.Sound:
        """
        Generate a simple mono sound procedurally.
        """
        sample_rate = config.AUDIO_FREQUENCY
        sample_count = int(sample_rate * duration)
        samples = []

        for i in range(sample_count):
            t = i / sample_rate

            if waveform == "sine":
                value = math.sin(2 * math.pi * frequency * t)

            elif waveform == "square":
                value = 1.0 if math.sin(2 * math.pi * frequency * t) >= 0 else -1.0

            elif waveform == "saw":
                cycle = (t * frequency) % 1.0
                value = 2.0 * cycle - 1.0

            elif waveform == "click":
                # Very short percussive thunk-like sound
                noise = random.uniform(-1.0, 1.0)
                tone = math.sin(2 * math.pi * frequency * t)
                value = (noise * 0.65) + (tone * 0.35)

            elif waveform == "noise_tone":
                noise = random.uniform(-1.0, 1.0) * 0.55
                tone = math.sin(2 * math.pi * frequency * t) * 0.45
                value = noise + tone

            else:
                value = math.sin(2 * math.pi * frequency * t)

            # Simple envelope
            if fade_out:
                envelope = max(0.0, 1.0 - (i / sample_count))
                value *= envelope
            else:
                # small click protection at beginning/end
                attack = min(1.0, i / max(1, int(sample_rate * 0.01)))
                release = min(1.0, (sample_count - i) / max(1, int(sample_rate * 0.01)))
                value *= min(attack, release)

            sample = int(max(-1.0, min(1.0, value)) * 32767 * config.MASTER_VOLUME * volume)
            samples.append(sample)

        raw = struct.pack("<" + "h" * len(samples), *samples)
        return pygame.mixer.Sound(buffer=raw)

    def _make_goal_sound(self) -> pygame.mixer.Sound:
        """
        Generate a short rising goal sound.
        """
        sample_rate = config.AUDIO_FREQUENCY
        duration = 0.42
        sample_count = int(sample_rate * duration)
        samples = []

        start_freq = 320
        end_freq = 760

        phase = 0.0
        for i in range(sample_count):
            progress = i / sample_count
            freq = start_freq + (end_freq - start_freq) * progress
            phase += (2 * math.pi * freq) / sample_rate

            tone = math.sin(phase)
            overtone = math.sin(phase * 0.5) * 0.35
            value = (tone * 0.7) + overtone

            envelope = max(0.0, 1.0 - progress)
            value *= envelope

            sample = int(max(-1.0, min(1.0, value)) * 32767 * config.MASTER_VOLUME * config.GOAL_VOLUME)
            samples.append(sample)

        raw = struct.pack("<" + "h" * len(samples), *samples)
        return pygame.mixer.Sound(buffer=raw)

    def update(self) -> None:
        """
        Per-frame housekeeping.
        """
        if self.impact_cooldown_frames > 0:
            self.impact_cooldown_frames -= 1

    def play_countdown_beep(self) -> None:
        if self.audio_enabled:
            self.sounds["countdown_beep"].play()

    def play_countdown_go(self) -> None:
        if self.audio_enabled:
            self.sounds["countdown_go"].play()

    def play_goal(self) -> None:
        if self.audio_enabled:
            self.sounds["goal"].play()

    def play_impact(self, strength: float = 1.0) -> None:
        """
        Play an impact sound with simple anti-spam control.
        """
        if not self.audio_enabled:
            return

        if self.impact_cooldown_frames > 0:
            return

        if strength >= 1.6:
            self.sounds["impact_hard"].play()
        else:
            self.sounds["impact_soft"].play()

        self.impact_cooldown_frames = 4

    def set_engine_active(self, active: bool) -> None:
        """
        Start/stop the engine loop-ish hum based on player throttle input.
        """
        if not self.audio_enabled or self.engine_channel is None:
            return

        if active:
            if not self.engine_channel.get_busy():
                self.engine_channel.play(self.sounds["engine"], loops=-1)
        else:
            if self.engine_channel.get_busy():
                self.engine_channel.stop()

    def set_boost_active(self, active: bool) -> None:
        """
        Start/stop the boost sound while boosting.
        """
        if not self.audio_enabled or self.boost_channel is None:
            return

        if active:
            if not self.boost_channel.get_busy():
                self.boost_channel.play(self.sounds["boost"], loops=-1)
        else:
            if self.boost_channel.get_busy():
                self.boost_channel.stop()

    def stop_all_loops(self) -> None:
        """
        Stop managed continuous sounds.
        """
        if not self.audio_enabled:
            return

        if self.engine_channel is not None:
            self.engine_channel.stop()

        if self.boost_channel is not None:
            self.boost_channel.stop()