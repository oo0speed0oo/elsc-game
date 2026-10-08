# ELSC Game — music and sound effects (GAME_SPEC §15 and §18.1).
# Music plays with pygame.mixer.music: one song at a time, streamed.
# Effects play with pygame.mixer.Sound, on top of the music.
# Everything loads from .ogg (what web browsers can play); an effect falls back
# to its .wav if the .ogg is missing.
# If there's no sound card, or a file is missing, the game just stays quiet.

import os
import sys

import pygame

import settings

SOUND_DIR = os.path.join(os.path.dirname(__file__), "assets", "sounds")

EFFECT_FILES = [
    "sfx_cursor", "sfx_select", "jingle_ready",
    "jingle_drumroll", "jingle_passed", "jingle_failed",
]


def start_mixer():
    """Call before pygame.init(). The buffer is how much sound is made at a time: big
    enough that the sound never runs dry while the game is busy (that crackles),
    small enough that effects still feel instant. Browsers need a bigger one, and
    play sound at 48000 Hz, so we match that (no extra converting while playing)."""
    web = sys.platform == "emscripten"
    buffer = settings.WEB_SOUND_BUFFER_SAMPLES if web else settings.SOUND_BUFFER_SAMPLES
    pygame.mixer.pre_init(48000 if web else 44100, -16, 2, buffer)


class Sound:
    def __init__(self, music_volume, fx_volume):
        self.working = pygame.mixer.get_init() is not None   # False = no sound card
        self.effects = {}           # name -> pygame.mixer.Sound (only the files that loaded)
        self.current_song = None    # the music file playing now, or None
        self.music_volume = music_volume
        self.fx_volume = fx_volume
        self.muted = False          # the Study Pocket's SOUND button: everything silent (GAME_SPEC §19.8)
        self.cut_offs = []          # (channel, sound, stop time in ms): effects playing "only the first N seconds"
        if self.working:
            for name in EFFECT_FILES:
                for ending in (".ogg", ".wav"):         # the .ogg first, the .wav if it's missing
                    path = os.path.join(SOUND_DIR, name + ending)
                    if not os.path.exists(path):
                        continue
                    try:
                        self.effects[name] = pygame.mixer.Sound(path)
                        break
                    except (pygame.error, FileNotFoundError):
                        pass        # broken file: try the next one (or stay silent)
        self.set_music_volume(music_volume)
        self.set_fx_volume(fx_volume)

    # -----------------------------------------------------------------------
    # Volume (0 to VOLUME_MAX, from the Options screen)
    # -----------------------------------------------------------------------
    def set_music_volume(self, volume):
        self.music_volume = volume
        if self.working:
            pygame.mixer.music.set_volume(self.loudness(volume))

    def set_fx_volume(self, volume):
        self.fx_volume = volume
        for effect in self.effects.values():
            effect.set_volume(self.loudness(volume))

    def loudness(self, volume):
        """A volume (0 to VOLUME_MAX) as pygame's 0.0 to 1.0, or 0 while muted."""
        return 0.0 if self.muted else volume / settings.VOLUME_MAX

    def set_muted(self, muted):
        """Sound off (True) or back on (False) for the whole game. The volumes
        chosen in Options are kept for when the sound comes back."""
        self.muted = muted
        self.set_music_volume(self.music_volume)
        self.set_fx_volume(self.fx_volume)

    # -----------------------------------------------------------------------
    # Effects
    # -----------------------------------------------------------------------
    def play(self, name, seconds=None):
        """Play a sound effect, for example sound.play("sfx_cursor").
        seconds = only play the start of it, this long (for example 0.4). That's done
        with a timer that stops the channel (see update()), because play(maxtime=...)
        may not work in a web browser."""
        if name not in self.effects:
            return
        effect = self.effects[name]
        channel = effect.play()
        if seconds is not None and channel is not None:
            self.cut_offs.append((channel, effect, pygame.time.get_ticks() + int(seconds * 1000)))

    def update(self):
        """Call every frame: stops the effects whose "first N seconds" are over."""
        now = pygame.time.get_ticks()
        still_playing = []
        for channel, effect, stop_at in self.cut_offs:
            if now < stop_at:
                still_playing.append((channel, effect, stop_at))
            elif channel.get_sound() is effect:
                channel.stop()      # (only if that channel is still playing this sound, not a newer one)
        self.cut_offs = still_playing

    def stop(self, name):
        """Cut a sound effect short."""
        if name in self.effects:
            self.effects[name].stop()

    # -----------------------------------------------------------------------
    # Music
    # -----------------------------------------------------------------------
    def play_music(self, name, restart=False):
        """Loop a song, for example "main_theme". If it's already playing,
        it just keeps going (so menus don't restart the song), unless
        restart=True (a new stage always starts its music from the top)."""
        if not self.working:
            return
        if self.current_song == name and pygame.mixer.music.get_busy() and not restart:
            return
        try:
            pygame.mixer.music.load(os.path.join(SOUND_DIR, name + ".ogg"))
            pygame.mixer.music.set_volume(self.loudness(self.music_volume))
            pygame.mixer.music.play(loops=-1)
            self.current_song = name
        except (pygame.error, FileNotFoundError):
            self.current_song = None    # missing or broken file: no music

    def pause_music(self):
        if self.working:
            pygame.mixer.music.pause()

    def resume_music(self):
        if self.working:
            pygame.mixer.music.unpause()

    def stop_music(self):
        if self.working:
            pygame.mixer.music.stop()
        self.current_song = None

    def fade_out_music(self, seconds):
        if self.working:
            pygame.mixer.music.fadeout(int(seconds * 1000))
        self.current_song = None
