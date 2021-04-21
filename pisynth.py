#%%
import supriya
from supriya.enums import DoneAction
import pisano
import math
import time
import scales
from datetime import datetime
import enum


def startServer():  
  s = supriya.Server.default()
  s.boot()
  return s

def createGroup():
  group = supriya.realtime.Group().allocate()
  return group

class Osc(enum.Enum):
  SinOsc=0
  VarSaw = 1
  Pulse = 2
  LFPulse = 3
  LFSaw = 4
  LFTri = 5
  Saw = 6

def osc_to_ugen(osc,builder):
  if osc.name == "SinOsc":
    return supriya.ugens.SinOsc.ar( frequency=builder['frequency'],) 
  if osc.name == "VarSaw":
    return supriya.ugens.VarSaw.ar( frequency=builder['frequency'],) 
  if osc.name == "Pulse":
    return supriya.ugens.Pulse.ar( frequency=builder['frequency'],width=0.5) 
  if osc.name == "LFPulse":
    return supriya.ugens.LFPulse.ar( frequency=builder['frequency'],width=0.5) 
  if osc.name == "LFSaw":
    return supriya.ugens.LFSaw.ar( frequency=builder['frequency']) 
  if osc.name == "LFTri":
    return supriya.ugens.LFTri.ar( frequency=builder['frequency']) 
  if osc.name == "Saw":
    return supriya.ugens.Saw.ar( frequency=builder['frequency']) 

class Filter(enum.Enum):
  LPF = 1
  BPF = 2
  HPF = 3
  TwoPole = 4
  RHPF = 5
  MoogFF = 6

def filter_to_ugen(filter,source,freq=440,mul=1,add=0):
  if filter.name == "LPF":
    return supriya.ugens.LPF.ar(source,freq,mul,add)
  if filter.name == "BPF":
    return supriya.ugens.BPF.ar(source,freq,mul,add)
  if filter.name == "HPF":
    return supriya.ugens.HPF.ar(source,freq,mul,add)
  if filter.name == "TwoPole":
    return supriya.ugens.TwoPole.ar(source,freq,mul,add)
  if filter.name == "RHPF":
    return supriya.ugens.RHPF.ar(source,freq,mul,add)
  if filter.name == "MoogFF":
    return supriya.ugens.MoogFF.ar(source,freq,mul,add)



def makeSynthDef(server,amp=0.0,freq=440.0,gate=1,perc_env = False,osc = Osc.SinOsc,is_delay=True,max_delay = 0.2,delay_time=0.2,decay_time=0.5):
  builder = supriya.synthdefs.SynthDefBuilder( amplitude=amp, frequency=freq, gate=gate, )
  with builder: 
    source = osc_to_ugen(osc,builder)
    envelope = supriya.ugens.EnvGen.ar( 
      done_action=supriya.DoneAction.NOTHING, 
      envelope=
        supriya.synthdefs.Envelope.percussive(attack_time=0.01,release_time=0.5,) 
        if perc_env else 
        supriya.synthdefs.Envelope.asr(attack_time=0.01,release_time=0.5,)
      ,
      gate=builder['gate'], ) 
    source = source * builder['amplitude']
    source = source * envelope 
    if is_delay:
      delay = supriya.ugens.AllpassC.ar(source,max_delay,delay_time,decay_time)
    else:
      delay = 1
    pan = supriya.ugens.Pan2.ar(source=source*delay )
    out = supriya.ugens.Out.ar( bus=0, source=pan, ) 
  synthdef = builder.build(name="test").allocate()
  server.sync()
  return synthdef

def toMidi(freq):
    return 69 + ( 12 * math.log( freq/440 ) / math.log(2) )

def toHz(freq):
  return 440*(2**((freq-69)/12))

def pisanoToMidi(series,low=0,high=115):
  # Normalize the values linearly between 20,100, this is the min max value of our scale
  linear_list = supriya.ugens.LinLin.ar(series.tolist(),min(series),max(series),low,high)
  # Floor all values
  notes_midi = [math.floor(key) for key in linear_list]
  return notes_midi

def pisanoToHz(series,):
  # Turn values back to Hz 
  notes_hz = [toHz(key) for key in series]
  return notes_hz

def pisanoToRythm(series):
  linear_list = supriya.ugens.LinLin.ar(series.tolist(),min(series),max(series),0,1)
  return [x for x in linear_list]



def create_synths(server):  
  synths = []
  group = createGroup()
  amount_of_synths = int(input("How many synths do you want (1-4):"))
  rootNote = 0
  for x in range(amount_of_synths):
    input_pis = int(input("Enter number for pisano: "))
    pis = pisano.getPisano(input_pis)
    # Take the first synths rootnote and use it as rootnote for the other synths
    if x == 0:
      rootNote = scales.getRootOffset(pisanoToMidi(pis))
    # Decide the scale of this synth according to the length of the pisano series
    scale = len(pis)%len(scales.Scales)

    # the first synth will play a higher melody and the last synth will have more bass
    lower_limit = 50*(1-(x*0.1))
    upper_limit = 90*(1-(x*0.1))

    # Create a score out of a piasno series
    synth_line = pisanoToHz(scales.quantizeScale(pisanoToMidi(pis,lower_limit,upper_limit), scales.Scales(scale),rootNote))
    # create rythmical score
    rythm = pisanoToRythm(pis)
    # Pick oscillator according to the length of the pisano series
    oscillator = len(pis)%len(Osc)
    # percussive or ASR envelope
    perc = True if (len(pis)%len(Osc)) % 2 else False
    synth_def = makeSynthDef(server,amp=0.75,perc_env=perc,osc=Osc(oscillator))
    synth = supriya.Synth(synth_def)
    group.append(synth)
    # Make a synth object with relevant variables so we can play them later
    synth_obj = {
      "synth":synth,
      "rythm":rythm,
      # Assign a certain interval between 0-1 to the synth
      # When the rythm score is in between that interval the synth will play a note
      "rythm_interval":(x*0.2,(x*0.2)+0.2),
      "score":synth_line,
      "counter":0,
      "pisano_period":input_pis,
      "scale":scales.Scales(scale).name,
      "oscillator":Osc(oscillator)
      }
    synths.append(synth_obj)

    notes = ["C","C#/Db","D","D#/Eb","E","F","F/Gb","G","G#/Ab","A","A#/Bb","B"]
  
    print("synth number",x+1)
    print("pisano",input_pis)
    print("scale",notes[rootNote],scales.Scales(scale).name)
    print("oscillator",Osc(oscillator).name)
    print(" ")
  return synths

## We search for the longest rythmscore

def play_synths(server, synths):
  time_div = int(input("Give time divisor n beats per second where n is:"))
  server.recorder.start(file_path="pisano_"+datetime.now().strftime("%d.%m_%H:%M:%S")+".wav", channel_count=2,header_format="WAV")

  # Get the longest score 
  longest_score  = max([len(x["rythm"]) for x in synths])
  for x in range(longest_score):
    for synth in synths:
      # If the rythm score has reached the end we start from the beginning
      rythm = synth["rythm"][x%len(synth["rythm"])]
      # Close the gate so we can play a new note
      server.send(["/n_set",synth["synth"].node_id,"gate", 0])
      # If the current value in the rythm score is between the rythm_interval we play a note
      if rythm > synth["rythm_interval"][0] and rythm < synth["rythm_interval"][1]:
        # Get the following note from the score
        
        server.send(["/n_set",synth["synth"].node_id,"frequency", synth["score"][synth["counter"]]])
        server.send(["/n_set",synth["synth"].node_id,"gate", 1])
        # increment counter
        synth["counter"] += 1
        # if counter is as long as the score we need to reset the counter
        if synth["counter"] == len(synth["score"]):
          synth["counter"] = 0
    time.sleep(1/time_div)

  server.recorder.stop()

  for synth in synths:
    synth["synth"].release()

#
# THIS IS THE MAIN WHERE WE RUN THE FUNCTIONS
#
server = startServer()
synths = create_synths(server)
play_synths(server,synths)

server.quit()




