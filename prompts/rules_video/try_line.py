# usage: try_line.py "candidate 1" "candidate 2" ...   -> prints ASR result for each
import sys, subprocess, numpy as np, re
from kokoro_onnx import Kokoro
from faster_whisper import WhisperModel
S="/tmp/claude-0/-home-user-rea-video/aab4cb51-a7e7-52e6-85f6-17b473411a46/scratchpad"
k=Kokoro(f"{S}/models/kokoro-v1.0.onnx",f"{S}/models/voices-v1.0.bin")
st=0.6*k.get_voice_style("am_michael")+0.4*k.get_voice_style("am_onyx")
m=WhisperModel("small.en",device="cpu",compute_type="int8")
norm=lambda t: re.sub(r"[^a-z' ]","",t.lower()).split()
for c in sys.argv[1:]:
    a,sr=k.create(c,voice=st,speed=0.92,lang="en-us")
    import soundfile as sf; sf.write(f"{S}/try.wav",a,sr)
    x=np.frombuffer(subprocess.run(["ffmpeg","-v","quiet","-i",f"{S}/try.wav","-f","f32le","-ac","1","-ar","16000","-"],capture_output=True).stdout,np.float32)
    h=" ".join(s.text for s in m.transcribe(x,beam_size=5,language="en")[0])
    print("OK " if norm(h)==norm(c) else "XX ", c, "->", h.strip())
