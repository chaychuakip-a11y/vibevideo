# 代码音效：章节翻页、关键词“盖章”轻响（0 积分）
import json, wave, numpy as np
ev = json.load(open("events.json")); SR, END = 48000, float(ev["end"])
out = np.zeros(int(SR * END)); rng = np.random.default_rng(3)
def put(at, y):
    i = int(SR * at); out[i:i + len(y)] += y[: len(out) - i]
def band(dur, g, center, shape):
    n = int(SR * dur); x = rng.standard_normal(n); X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR)
    X *= np.exp(-((np.log(f + 1) - np.log(center)) ** 2) / .4); y = np.fft.irfft(X, n); y /= np.abs(y).max()
    return g * y * shape(np.arange(n) / n)
def tick(g=.22):
    n = int(SR * .12); t = np.arange(n) / SR
    return g * (np.sin(2 * np.pi * 880 * t) * .6 + np.sin(2 * np.pi * 1320 * t) * .4) * np.exp(-t * 40)
for at in ev["pages"]: put(at, band(.5, .22, 3500, lambda u: np.exp(-u * 6) * (1 - np.exp(-u * 80))))
m = ev["marks"]
for k in ["h_stall", "p_third", "p_twothird", "p_simres", "r_cmp2", "r_burst", "a_70", "a_65", "m_slow", "m_regret", "w_idle", "w_h5", "s_1", "s_2", "s_3", "s_4", "s_5", "f_single", "e_title"]:
    put(m[k], tick())
pcm = (np.clip(out, -1, 1) * 32767 * .8).astype(np.int16)
with wave.open("sfx.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("sfx ok")
