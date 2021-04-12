#%%
import supriya
from supriya.enums import DoneAction
import pisano
import math
import time
import scales

def startServer():  
  s = supriya.Server.default()
  s.boot()
  return s

def createGroup():
  group = supriya.realtime.Group().allocate()
  return group

def makeSynthDef(server):
  builder = supriya.synthdefs.SynthDefBuilder( amplitude=1.0, frequency=440.0, gate=1.0, )
  with builder: 
    source = supriya.ugens.SinOsc.ar( frequency=builder['frequency'],) 
    envelope = supriya.ugens.EnvGen.ar( 
      done_action=supriya.DoneAction.NOTHING, 
      envelope=supriya.synthdefs.Envelope.percussive(attack_time=0.01,release_time=0.5,),
      gate=builder['gate'], ) 
    source = source * builder['amplitude']
    source = source * envelope 
    #delay = supriya.ugens.AllpassC.ar(source,0.2,0.2,0.5)
    pan = supriya.ugens.Pan2.ar(source=source)#*delay )
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


#%%

server = startServer()
group = createGroup()

#%%

sDef = makeSynthDef(server)
synth = supriya.Synth(sDef)
synth2 = supriya.Synth(sDef)


#%%
group.append(synth)
group.append(synth2)
#%%

synth_line = pisanoToHz(scales.quantizeScale(pisanoToMidi(pisano.getPisano(436),40,70), scales.Scales.Phrygian_Minor))
synth_line2 = pisanoToHz(scales.quantizeScale(pisanoToMidi(pisano.getPisano(436),15,40), scales.Scales.Pentatonic_Minor))
rythm = pisanoToRythm(pisano.getPisano(42))

#%%

#server.recorder.start(file_path="test2.wav", channel_count=2,header_format="WAV")

#Counters for synth 1 and 2 
sC =0
sC2 =0
print(len(rythm))
for x in rythm:
  # Have to close the gate so i can trigger it again
  server.send(["/n_set",synth.node_id,"gate", 0])
  server.send(["/n_set",synth2.node_id,"gate", 0])
  
  # If the rythm track value is lower than 0.25 play the next note on synth 1
  if x < 0.35:
    server.send(["/n_set",synth.node_id,"frequency", synth_line[sC]])
    server.send(["/n_set",synth.node_id,"gate", 1])
    sC += 1
  # If the rythm track value is higher than 0.75 play the next note on synth 2
  if x > 0.75:
    server.send(["/n_set",synth2.node_id,"frequency", synth_line2[sC2]])
    server.send(["/n_set",synth2.node_id,"gate", 1])
  #server.send(["/n_get",synth.node_id,"gate"])
    sC2 += 1
  
  # If the counters have reached the end of the list reset them to 0
  if sC == len(synth_line)-1:
    sC = 0
  if sC2 == len(synth_line2)-1:
    sC2 = 0
  time.sleep(1/4)

synth.release()
synth2.release()

#server.recorder.stop()

#%%
#server.recorder.stop()
response = server.query_remote_nodes(include_controls=True)
print(response)
#%%
synth.release()
synth2.release()
#%%
server.quit()


# %%
server.recorder.is_recording

# %%
import supriya
supriya.Scale

# %%
