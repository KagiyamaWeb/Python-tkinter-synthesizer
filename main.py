import json
import numpy as np

from tkinter import Tk, Label, Button
from notes.notelist import notelist
from pygame import mixer
import pygame as pg

from synth_piano import piano, saw_synth, synth, organ
from consts import BUFFER, SAMPLE_RATE, DURATION


window = Tk()  
window.title('KagiPiano')
window.geometry("1640x800") 
font = ('calibre', 10, 'normal')

lbl = Label(window, font=("Arial", 12))
lbl.grid(columnspan=4, row=0, sticky="w")

mixer.init()

bkey_row = 2
wkey_row = 3

key_width = 4
key_height = 10


def play_sound(note: str):
    with open('notes/notes.json', 'r') as f:
        notes_dict = json.load(f)

    print(note)
    freq = notes_dict[note][0]
    gen = saw_synth(freq)
    iter(gen)
    sound = [next(gen) * 32767  for _ in range(int(SAMPLE_RATE * DURATION))]
    sound = np.asarray([sound, sound]).T.astype(np.int16)
    sound = pg.sndarray.make_sound(sound.copy())
    sound.set_volume(0.13)
    sound.play()

column = 0
for i in range(24, 51):
    note = notelist[i]
    bg = "white"
    fg = "black"
    row=wkey_row
    if "#" in note:
        bg = "black"
        fg = "white"
        row=bkey_row
    key = Button(window, width=key_width, height=key_height, text=note, command= lambda i=i: play_sound(notelist[i]), bg=bg, fg=fg)
    key.grid(column=column, columnspan=2,row=row)
    column += 2

window.mainloop()

