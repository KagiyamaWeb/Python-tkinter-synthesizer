import pygame as pg
import numpy as np
import consts
from modulation import WaveAdder, ADSREnvelope, ModulatedOscillator, Chain, amp_mod, ModulatedVolume
from oscillator import SineOscillator, TriangleOscillator, SawtoothOscillator, SquareOscillator


def piano(frequency, duration=consts.DURATION, sampling_rate=consts.SAMPLE_RATE):
    frames = int(duration*sampling_rate)
    arr = np.cos(2*np.pi*frequency*np.linspace(0,duration, frames))
    arr = np.cumsum(np.clip(arr*10, -1, 1))
    arr = arr+np.sin(2*np.pi*frequency*np.linspace(0,duration, frames))
    arr = arr/max(np.abs(arr))
    sound = np.asarray([32767*arr,32767*arr]).T.astype(np.int16)
    sound = pg.sndarray.make_sound(sound.copy())
    return sound


def synth(freq=0):
    gen = WaveAdder(
            ModulatedOscillator(
                TriangleOscillator(freq),
                ADSREnvelope(attack_duration=0.1, decay_duration=0, sustain_level=0, \
                             release_duration=0.7),
            ),
            ModulatedOscillator(
                SineOscillator(freq*2),
                ADSREnvelope(attack_duration=0.1, decay_duration=0, sustain_level=0, \
                             release_duration=0.7),
            ),
            ModulatedOscillator(
                SineOscillator(freq*4),
                ADSREnvelope(attack_duration=0.1, decay_duration=0, sustain_level=0, \
                             release_duration=0.7),
            )
    )
    return gen


def organ(freq=0):
    gen = WaveAdder(

            ModulatedOscillator(
                SineOscillator(freq),
                ADSREnvelope(attack_duration=0.1, decay_duration=0.1, sustain_level=0.7, \
                             release_duration=0.4),
            ),
            ModulatedOscillator(
                SineOscillator(freq*2),
                ADSREnvelope(attack_duration=0.1, decay_duration=0.1, sustain_level=0.7, \
                             release_duration=0.4),
            ),
            ModulatedOscillator(
                SineOscillator(freq*4),
                ADSREnvelope(attack_duration=0.1, decay_duration=0.1, sustain_level=0.7, \
                             release_duration=0.4),
            )
    )
    return gen


def saw_synth(freq=0):
    gen = ModulatedOscillator(
        Chain(
        WaveAdder(
            ModulatedOscillator(
                TriangleOscillator(freq),
                ADSREnvelope(attack_duration=0.33, decay_duration=1.11, sustain_level=0, \
                             release_duration=0.25),
                amp_mod=amp_mod
            ),
            ModulatedOscillator(
                TriangleOscillator(freq*2),
                ADSREnvelope(attack_duration=0.33, decay_duration=1.11, sustain_level=0, \
                             release_duration=0.25),
                amp_mod=amp_mod
            ),
            ModulatedOscillator(
                TriangleOscillator(freq*4),
                ADSREnvelope(attack_duration=0.33, decay_duration=1.11, sustain_level=0, \
                             release_duration=0.25),
                amp_mod=amp_mod
            ),
        ),
        ModulatedVolume(
            ModulatedOscillator(
                SawtoothOscillator(1),
                ADSREnvelope(attack_duration=0,  decay_duration=1, sustain_level=0),
                amp_mod=amp_mod
                )
            )
        )
    )

    return gen