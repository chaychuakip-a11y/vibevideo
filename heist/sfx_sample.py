# 全部代码合成的声音设计：环境底噪、显示器嗡声、心跳、门铃、开门、脚步、转身、金属“咔”、耳鸣、闷脚步
import json, wave, numpy as np
ev = json.load(open("events.json")); SR, END = 48000, float(ev["end"])
N = int(SR * END); L = np.zeros(N); R = np.zeros(N); t = np.arange(N) / SR
rng = np.random.default_rng(1990)
def put(at, y, g=1.0, pan=0.0):
    i = int(SR * at); y = y[: max(0, N - i)] * g
    L[i:i + len(y)] += y * (1 - max(0, pan)); R[i:i + len(y)] += y * (1 + min(0, pan))
def bandnoise(n, center, width):
    x = rng.standard_normal(n); X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR)
    X *= np.exp(-((np.log(f + 1) - np.log(center)) ** 2) / width); y = np.fft.irfft(X, n); return y / (np.abs(y).max() + 1e-9)
def lowpass(y, fc):
    Y = np.fft.rfft(y); f = np.fft.rfftfreq(len(y), 1 / SR); Y *= 1 / (1 + (f / fc) ** 4); return np.fft.irfft(Y, len(y))
def env(n, a, d): u = np.arange(n) / SR; return (1 - np.exp(-u / a)) * np.exp(-u / d)
tension = np.select([t < 3, t < 6, t < 9.2, t < 11.5], [.1, .3, .65, 1.0], .5)
# 环境底噪：低频嗡 + 暗噪声，随紧张度微升；黑暗段变闷
drone = .05 * np.sin(2 * np.pi * 55 * t) + .03 * np.sin(2 * np.pi * 82.4 * t + np.sin(t * .3))
room = bandnoise(N, 180, 1.2) * .03
amb = (drone + room) * (.7 + .6 * tension)
L += amb; R += amb
# 显示器 60Hz 电流声（只在值班台段）
hum = (.012 * np.sin(2 * np.pi * 60 * t) + .006 * np.sin(2 * np.pi * 120 * t)) * np.clip((6.0 - t) / .3, 0, 1)
L += hum; R += hum
# 心跳：每拍一个低频闷响，第二下稍轻
beats = ev["beats"]
for k, b in enumerate(beats):
    n = int(SR * .3); u = np.arange(n) / SR
    y = np.sin(2 * np.pi * 52 * u * (1 - u * .8)) * env(n, .004, .07)
    g = (.25 + .55 * float(np.interp(b, t, tension))) * (1 if k % 2 == 0 else .7)
    put(b, y, g)
# 门铃（3.2 秒）：方波，略微滤波
n = int(SR * .75); u = np.arange(n) / SR
buzz = lowpass(np.sign(np.sin(2 * np.pi * 330 * u)) * .5 + np.sign(np.sin(2 * np.pi * 495 * u)) * .25, 2500) * np.clip(u / .01, 0, 1) * np.clip((.75 - u) / .03, 0, 1)
put(3.2, buzz, .16, .3)
# 按钮（5.5）+ 电磁锁“咔哒”（5.6）+ 门打开（6.0）
def click(g, fc=4000): n = int(SR * .04); return bandnoise(n, fc, .3) * env(n, .0005, .006) * g
put(5.5, click(.5)); put(5.62, click(.7, 1800), 1, -.2)
n = int(SR * 1.6); u = np.arange(n) / SR
creak = bandnoise(n, 700, .08) * (np.sin(2 * np.pi * (3 + 2 * u) * u) * .5 + .5) * env(n, .2, .8)
put(6.0, click(.9, 900)); put(6.05, creak, .18, -.1)
# 脚步：两个人，交错，越来越近（越来越响）
for k, s in enumerate(np.arange(6.7, 9.1, .26)):
    n = int(SR * .12); y = lowpass(bandnoise(n, 400, .6), 1500) * env(n, .002, .03)
    put(float(s), y, .12 + .5 * (s - 6.7) / 2.4, .25 if k % 2 else -.25)
# 转身：低频呼啸
n = int(SR * 1.1); u = np.arange(n) / SR
put(9.2, bandnoise(n, 400, .5) * np.sin(np.pi * u / 1.1) ** 2, .22)
# 金属“咔”：手铐棘轮，几下短促的高频
for k in range(6):
    n = int(SR * .025); y = bandnoise(n, 5200 - k * 250, .15) * env(n, .0003, .005)
    put(10.55 + k * .028, y, .8 - k * .1, .1)
# 耳鸣：咔之后一段很轻的高频，慢慢消失
n = int(SR * 2.4); u = np.arange(n) / SR
put(10.6, np.sin(2 * np.pi * 6200 * u) * np.exp(-u / 1.1) * np.clip(u / .05, 0, 1), .035)
# 黑暗：楼上闷闷的脚步（低通，很远）
for s in [12.1, 12.55, 13.0, 13.45]:
    n = int(SR * .25); y = lowpass(bandnoise(n, 120, .6), 300) * env(n, .004, .07)
    put(s, y, .35)
# 结尾淡出
fadeout = np.clip((END - t) / 1.0, 0, 1) * np.clip(t / .5, 0, 1)
L *= fadeout; R *= fadeout
st = np.stack([L, R], 1); st /= max(1e-9, np.abs(st).max()) / .89
with wave.open("sound.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())
print("sound ok", len(beats), "beats")
