# 代码音效：章节翻图纸、红铅笔批注的沙沙声（0 积分）
import json, wave, numpy as np
ev = json.load(open("events.json")); SR, END = 48000, float(ev["end"])
out = np.zeros(int(SR * END)); rng = np.random.default_rng(11)
def put(at, y):
    i = int(SR * at); out[i:i + len(y)] += y[: len(out) - i]
def band(dur, g, center, shape, width=.4):
    n = int(SR * dur); x = rng.standard_normal(n); X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR)
    X *= np.exp(-((np.log(f + 1) - np.log(center)) ** 2) / width); y = np.fft.irfft(X, n); y /= np.abs(y).max()
    return g * y * shape(np.arange(n) / n)
page = lambda: band(.55, .22, 3200, lambda u: np.exp(-u * 6) * (1 - np.exp(-u * 80)))
# 铅笔：几下短促的高频沙沙
def pencil():
    y = np.zeros(int(SR * .7))
    for k in range(4):
        s = band(.09, .09, 5200, lambda u: np.sin(np.pi * u), .2); i = int(SR * (.05 + k * .14)); y[i:i + len(s)] += s
    return y
for at in ev["pages"]: put(at, page())
m = ev["marks"]
for k in ["h_before", "h_q", "w_700", "w_public", "w_sweet", "a_33", "a_bridge", "a_oldest", "a_lacus", "a_canals", "a_wells", "a_canal", "q_depth", "q_3200", "q_meet", "c_80k", "c_reserve", "l_17", "l_hard", "d_up", "d_su", "d_wozi", "s_5", "s_combo", "s_before", "e_think"]:
    put(m[k] + .8, pencil())
pcm = (np.clip(out, -1, 1) * 32767 * .8).astype(np.int16)
with wave.open("sfx.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("sfx ok")
