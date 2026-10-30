# 代码合成的哈欠"呼气"音效：带通噪声 + 起落包络，0 积分
import numpy as np, wave
SR, END = 48000, 14.0
rng = np.random.default_rng(7)
out = np.zeros(int(SR * END))
def breath(at, gain, dur=1.25):
    n = int(SR * dur); x = rng.standard_normal(n)
    X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR)
    X *= np.exp(-((np.log(f + 1) - np.log(700)) ** 2) / 0.5)   # 以 700Hz 为中心的柔和带通
    y = np.fft.irfft(X, n); y /= np.abs(y).max()
    tt = np.arange(n) / n
    env = np.where(tt < .35, (tt / .35) ** 2, np.exp(-(tt - .35) * 5))
    i = int(SR * at); out[i:i + n] += (y * env * gain)[: len(out) - i]
times = [(1.2, .5)] + [(2.9 + .55 * k, .32) for k in range(6)] + [(7.75, .35), (8.0, .3), (8.05, .3), (9.0, .12), (12.6, .55)]
for at, g in times: breath(at, g)
pcm = (np.clip(out, -1, 1) * 32767 * .7).astype(np.int16)
with wave.open("sfx.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
