# 按 yawns.json（[开始秒, 时长, 强度]）合成每个哈欠的柔和呼气声
import json, wave, numpy as np
SR, END = 48000, 154.0
rng = np.random.default_rng(7)
out = np.zeros(int(SR * END))
def breath(at, dur, gain):
    n = int(SR * max(1.2, dur)); x = rng.standard_normal(n)
    X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR)
    X *= np.exp(-((np.log(f + 1) - np.log(700)) ** 2) / 0.5)
    y = np.fft.irfft(X, n); y /= np.abs(y).max()
    tt = np.arange(n) / n
    env = np.where(tt < .35, (tt / .35) ** 2, np.exp(-(tt - .35) * 5))
    i = int(SR * at); out[i:i + n] += (y * env * gain)[: len(out) - i]
ev = json.load(open("yawns.json"))
for at, dur, k in ev: breath(at, dur, .32 * k * (1.4 if at in (1.5, 147.6) else 1))
pcm = (np.clip(out, -1, 1) * 32767 * .7).astype(np.int16)
with wave.open("sfx_full.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print(len(ev), "yawns")
