#%%
import enum

class Scales(enum.Enum):
  Major = 0
  Dorian = 1
  Phrygian = 2
  Lydian = 3
  Mixolydian = 4
  Minor = 5
  Locrian = 6
  Harmonic_Minor = 7
  Phrygian_Minor = 8
  Pentatonic_Minor = 9
  Pentatonic_Major = 10
  Japanese = 11
  Egyptian = 12
  Man_Gong = 13

def getScalePattern(scale):
  if scale.name == "Major":
    return [0,2,4,5,7,9,11]
  if scale.name == "Dorian":
    return[0,2,3,5,7,9,10]
  if scale.name == "Phrygian":
    return [0,1,3,5,7,8,10]
  if scale.name == "Lydian":
    return [0,2,4,6,7,9,11]
  if scale.name == "Mixolydian":
    return [0,2,4,5,7,9,10]
  if scale.name == "Minor":
    return [0,2,3,5,7,8,10]
  if scale.name == "Locrian":
    return [0,1,3,5,6,8,10]
  if scale.name == "Harmonic_Minor":
    return [0,2,3,5,7,8,11]
  if scale.name == "Phrygian_Minor":
    return [0,1,4,5,7,8,10]
  if scale.name == "Pentatonic_Minor":
    return [0,3,5,7,10]
  if scale.name == "Pentatonic_Major":
    return [0,2,4,7,9]
  if scale.name == "Japanese":
    return [0,1,5,7,8]
  if scale.name == "Egyptian":
    return [0,2,5,7,10]
  if scale.name == "Man_Gong":
    return [0,3,5,8,10]
  if scale.name == "Ritsusen":
    return [0,2,5,7,9]

# Floor the note to the nearest lower correct scale note
def fixNote(note,pattern):
  octave = (note // 12) * 12
  degree = note % 12
  if degree in pattern:
    return note 
  else:
    lower_notes = list(filter(lambda x: x < degree ,pattern))
    return lower_notes[-1] + octave 

# Gets the root note of a pisano series according to the most common note
def getRootOffset(input):
  offset = max(set(input), key= input.count)%12
  return offset

def quantizeScale(input, scale, offset):
  '''
    Takes as input as list of midi notes and a scale see Scales enum
    Return a list with the values floored to the closest key in the scale
  '''
  pattern = getScalePattern(scale)
  output = list(map(lambda x: fixNote(x,pattern)+offset,input))
  return output


# %%
