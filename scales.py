#%%
import enum

class Scales(enum.Enum):
  Major = 1
  Dorian = 2
  Phrygian = 3
  Lydian = 4
  Mixolydian = 5
  Minor = 6
  Locrian = 7
  Harmonic_Minor = 8
  Phrygian_Minor = 9
  Pentatonic_Minor = 10
  Pentatonic_Major = 11

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

# Floor the note to the nearest lower correct scale note
def fixNote(note,pattern):
  octave = (note // 12) * 12
  degree = note % 12
  if degree in pattern:
    return note 
  else:
    lower_notes = list(filter(lambda x: x < degree ,pattern))
    return lower_notes[-1] + octave 


def quantizeScale(input, scale, root_offset = True):
  '''
    Takes as input as list of midi notes and a scale see Scales enum
    Return a list with the values floored to the closest key in the scale
  '''
  pattern = getScalePattern(scale)
  if root_offset:
    # Offsets the output list according to the most frequent value in the list being the root note
    offset = max(set(input), key= input.count)%12
  else:
    offset = 0
  output = list(map(lambda x: fixNote(x,pattern)+offset,input))
  return output


# %%
