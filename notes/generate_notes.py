import json
from notes.notelist import notelist

keylist = '123456789qwertyuioasdfghjklzxcvbnm,.'
notes_file = open("notes/notelist.txt")
file_contents = notes_file.read()
notes_file.close()

notes = {}      # dict to store samples
freq = 16.3516 # start frequency

i = 0
for note in notelist:
    mod = int(i/36)
    key = keylist[i-mod*36]+str(mod) 
    notes[note] = (freq, key)

    freq = freq * 2 ** (1/12)
    i += 1


with open("notes/notes.json", "w") as f:
    json_notes = json.dumps(notes, indent=4)
    f.write(json_notes)