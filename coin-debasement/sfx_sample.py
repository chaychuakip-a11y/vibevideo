# 代码音效：铜钱叮当、落印闷响、钱流动的沙沙声、木桶滑动（0 积分）
import json, wave, numpy as np
SR, END = 48000, 15.0
out = np.zeros(int(SR * END)); rng = np.random.default_rng(5)
def put(at, y):
    i = int(SR * at); out[i:i + len(y)] += y[: len(out) - i]
def clink(g=.28, k=0):
    n = int(SR * .45); t = np.arange(n) / SR
    fs = [2350 + 40 * k, 3720 + 55 * k, 5120]   # 不谐和泛音 = 金属感
    return g * sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in zip(fs, [9, 13, 18])) / 2
def thump(g=.7):
    n = int(SR * .35); t = np.arange(n) / SR
    return g * (np.sin(2 * np.pi * 70 * t) * np.exp(-t * 16) + .3 * rng.standard_normal(n) * np.exp(-t * 60))
def swish(dur, g=.18, center=1800):
    n = int(SR * dur); x = rng.standard_normal(n); X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR)
    X *= np.exp(-((np.log(f + 1) - np.log(center)) ** 2) / .4); y = np.fft.irfft(X, n); y /= np.abs(y).max()
    tt = np.arange(n) / n; return g * y * np.sin(np.pi * tt)
ev = json.load(open("events.json"))
for k, at in enumerate(ev["clinks"]): put(at, clink(k=k))
for at in ev["seals"]: put(at, thump())
put(ev["flow"], swish(.9)); put(ev["slide"], swish(1.2, .14, 500))
pcm = (np.clip(out, -1, 1) * 32767 * .8).astype(np.int16)
with wave.open("sfx.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
