# 代码音效：铜钱叮当、落印闷响、钱/汤流动的沙沙声、章节翻纸声（0 积分）
import json, wave, numpy as np
ev = json.load(open("events_full.json"))
SR, END = 48000, float(ev["end"])
out = np.zeros(int(SR * END)); rng = np.random.default_rng(5)
def put(at, y):
    i = int(SR * at); out[i:i + len(y)] += y[: len(out) - i]
def clink(g=.26, k=0):
    n = int(SR * .45); t = np.arange(n) / SR
    fs = [2350 + 40 * (k % 6), 3720 + 55 * (k % 6), 5120]
    return g * sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in zip(fs, [9, 13, 18])) / 2
def thump(g=.7):
    n = int(SR * .35); t = np.arange(n) / SR
    return g * (np.sin(2 * np.pi * 70 * t) * np.exp(-t * 16) + .3 * rng.standard_normal(n) * np.exp(-t * 60))
def band(dur, g, center, shape):
    n = int(SR * dur); x = rng.standard_normal(n); X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR)
    X *= np.exp(-((np.log(f + 1) - np.log(center)) ** 2) / .4); y = np.fft.irfft(X, n); y /= np.abs(y).max()
    return g * y * shape(np.arange(n) / n)
swish = lambda: band(.9, .16, 1800, lambda u: np.sin(np.pi * u))
page = lambda: band(.5, .2, 3500, lambda u: np.exp(-u * 6) * (1 - np.exp(-u * 80)))
for k, at in enumerate(ev["clinks"]): put(at, clink(k=k))
for at in ev["seals"]: put(at, thump())
for at in ev["swish"]: put(at, swish())
for at in ev["pages"]: put(at, page())
pcm = (np.clip(out, -1, 1) * 32767 * .8).astype(np.int16)
with wave.open("sfx_full.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("sfx ok")
