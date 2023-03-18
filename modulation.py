import itertools
from collections.abc import Iterable

from consts import SAMPLE_RATE


class ADSREnvelope:
    def __init__(self, attack_duration=0.05, decay_duration=0.2, sustain_level=0.7, \
                 release_duration=0.3, sample_rate=SAMPLE_RATE):
        self.attack_duration = attack_duration
        self.decay_duration = decay_duration
        self.sustain_level = sustain_level
        self.release_duration = release_duration
        self._sample_rate = sample_rate
        
    def get_ads_stepper(self):
        steppers = []
        if self.attack_duration > 0:
            steppers.append(itertools.count(start=0, \
                step= 1 / (self.attack_duration * self._sample_rate)))
        if self.decay_duration > 0:
            steppers.append(itertools.count(start=1, \
            step=-(1 - self.sustain_level) / (self.decay_duration  * self._sample_rate)))
        while True:
            l = len(steppers)
            if l > 0:
                val = next(steppers[0])
                if l == 2 and val > 1:
                    steppers.pop(0)
                    val = next(steppers[0])
                elif l == 1 and val < self.sustain_level:
                    steppers.pop(0)
                    val = self.sustain_level
            else:
                val = self.sustain_level
            yield val
    
    def get_r_stepper(self):
        val = 1
        if self.release_duration > 0:
            release_step = - self.val / (self.release_duration * self._sample_rate)
            stepper = itertools.count(self.val, step=release_step)
        else:
            val = -1
        while True:
            if val <= 0:
                self.ended = True
                val = 0
            else:
                val = next(stepper)
            yield val
    
    def __iter__(self):
        self.val = 0
        self.ended = False
        self.stepper = self.get_ads_stepper()
        return self
    
    def __next__(self):
        self.val = next(self.stepper)
        return self.val
        
    def trigger_release(self):
        self.stepper = self.get_r_stepper()


class ModulatedOscillator:
    def __init__(self, oscillator, *modulators, amp_mod=None, freq_mod=None, phase_mod=None):
        self.oscillator = oscillator
        self.modulators = modulators # list
        self.amp_mod = amp_mod
        self.freq_mod = freq_mod
        self.phase_mod = phase_mod
        self._modulators_count = len(modulators)
    
    def __iter__(self):
        iter(self.oscillator)
        [iter(modulator) for modulator in self.modulators]
        return self
    
    def _modulate(self, mod_vals):
        if self.amp_mod is not None:
            new_amp = self.amp_mod(self.oscillator.init_amp, mod_vals[0])
            self.oscillator.amp = new_amp
            
        if self.freq_mod is not None:
            if self._modulators_count == 2:
                mod_val = mod_vals[1]
            else:
                mod_val = mod_vals[0]
            new_freq = self.freq_mod(self.oscillator.init_freq, mod_val)
            self.oscillator.freq = new_freq
            
        if self.phase_mod is not None:
            if self._modulators_count == 3:
                mod_val = mod_vals[2]
            else:
                mod_val = mod_vals[-1]
            new_phase = self.phase_mod(self.oscillator.init_phase, mod_val)
            self.oscillator.phase = new_phase
    
    def trigger_release(self):
        tr = "trigger_release"
        for modulator in self.modulators:
            if hasattr(modulator, tr):
                modulator.trigger_release()
        if hasattr(self.oscillator, tr):
            self.oscillator.trigger_release()
            
    @property
    def ended(self):
        e = "ended"
        ended = []
        for modulator in self.modulators:
            if hasattr(modulator, e):
                ended.append(modulator.ended)
        if hasattr(self.oscillator, e):
            ended.append(self.oscillator.ended)
        return all(ended)

    def __next__(self):
        mod_vals = [next(modulator) for modulator in self.modulators]
        self._modulate(mod_vals)
        return next(self.oscillator)


class Chain:
    def __init__(self, generator, *modifiers):
        self.generator = generator
        self.modifiers = modifiers
        
    def __getattr__(self, attr):
        val = None
        if hasattr(self.generator, attr):
            val = getattr(self.generator, attr)
        else:
            for modifier in self.modifiers:
                if hasattr(modifier, attr):
                    val = getattr(modifier, attr)
                    break
            else:
                raise AttributeError(f"attribute '{attr}' does not exist")
        return val
    
    def trigger_release(self):
        tr = "trigger_release"
        if hasattr(self.generator, tr):
            self.generator.trigger_release()
        for modifier in self.modifiers:
            if hasattr(modifier, tr):
                modifier.trigger_release()
                
    @property
    def ended(self):
        ended = []; e = "ended"
        if hasattr(self.generator, e):
            ended.append(self.generator.ended)
        ended.extend([m.ended for m in self.modifiers if hasattr(m, e)])
        return all(ended)
    
    def __iter__(self):
        iter(self.generator)
        [iter(mod) for mod in self.modifiers if hasattr(mod, "__iter__")]
        return self
        
    def __next__(self):
        val = next(self.generator)
        [next(mod) for mod in self.modifiers if hasattr(mod, "__iter__")]
        for modifier in self.modifiers:
            val = modifier(val)
        return val



class WaveAdder:
    def __init__(self, *generators, stereo=False):
        self.generators = generators
        self.stereo = stereo
        
    def _mod_channels(self, _val):
        val = _val
        if isinstance(_val, (int, float)) and self.stereo:
            val = (_val, _val)
        elif isinstance(_val, Iterable) and not self.stereo:
            val = sum(_val)/len(_val)
        return val
    
    def trigger_release(self):
        [gen.trigger_release() for gen in self.generators if hasattr(gen, "trigger_release")]
    
    @property
    def ended(self):
        ended = [gen.ended for gen in self.generators if hasattr(gen, "ended")]
        return all(ended)
    
    def __iter__(self):
        [iter(gen) for gen in self.generators]
        return self
            
    def __next__(self):
        vals = [self._mod_channels(next(gen)) for gen in self.generators]
        if self.stereo:
            l, r = zip(*vals)
            val = (sum(l)/len(l), sum(r)/len(r))
        else:
            val = sum(vals)/ len(vals)
        return val


def amp_mod(init_amp, env):
    return env * init_amp
    
def freq_mod(init_freq, env, mod_amt=0.01, sustain_level=0.7):
    return init_freq + ((env - sustain_level) * init_freq * mod_amt)


class Panner:
    def __init__(self, r=0.5):
        self.r = r
        
    def __call__(self, val):
        r = self.r * 2
        l = 2 - r
        return (l * val, r * val)


class ModulatedPanner(Panner):
    def __init__(self, modulator):
        super().__init__(r=0)
        self.modulator = modulator
        
    def __iter__(self):
        iter(self.modulator)
        return self
    
    def __next__(self):
        self.r = (next(self.modulator) + 1) / 2
        return self.r


class Volume:
    def __init__(self, amp=1.):
        self.amp = amp
        
    def __call__(self, val):
        _val = None
        if isinstance(val, Iterable):
            _val = tuple(v * self.amp for v in val)
        elif isinstance(val, (int, float)):
            _val = val * self.amp
        return _val


class ModulatedVolume(Volume):
    def __init__(self, modulator):
        super().__init__(0.)
        self.modulator = modulator
        
    def __iter__(self):
        iter(self.modulator)
        return self
    
    def __next__(self):
        self.amp = next(self.modulator)
        return self.amp
    
    def trigger_release(self):
        if hasattr(self.modulator, "trigger_release"):
            self.modulator.trigger_release()
    
    @property
    def ended(self):
        ended = False
        if hasattr(self.modulator, "ended"):
            ended = self.modulator.ended
        return ended