# 代码音效：负载“咔哒”、关机下滑音 + 低频闷响、开机提示音（0 积分）
import json, wave, numpy as np
SR, END = 48000, 158.0
out = np.zeros(int(SR * END)); rng = np.random.default_rng(3)
def put(at, y):
    i = int(SR * at); out[i:i + len(y)] += y[: len(out) - i]
def click(g=.35):
    n = int(SR * .05); t = np.arange(n) / SR
    return g * rng.standard_normal(n) * np.exp(-t * 120)
def powerdown(g=.6):
    n = int(SR * .9); t = np.arange(n) / SR
    f = 900 * np.exp(-t * 4) + 60                      # 下滑音
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.5) * .5
    thump = np.sin(2 * np.pi * 48 * t) * np.exp(-t * 7)
    return g * (tone + thump)
def chime(g=.3):
    n = int(SR * 1.2); t = np.arange(n) / SR
    return g * sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in [(660, 3), (990, 4), (1320, 5)]) / 2
ev = json.load(open("events.json"))
put(7.0, powerdown())
for s, _ in ev["loads"]: put(s, click())
for b0, _ in ev["black"]: put(b0, powerdown())
put(129.0, chime())
put(151.0, click(.6))   # 盖章
pcm = (np.clip(out, -1, 1) * 32767 * .8).astype(np.int16)
with wave.open("sfx.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("ok")
