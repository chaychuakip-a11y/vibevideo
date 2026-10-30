# 完整版声音设计（全部代码合成，无配乐）
import json, wave, numpy as np
ev = json.load(open("events_full.json")); S = ev["S"]; SR, END = 48000, float(ev["end"])
N = int(SR * END); L = np.zeros(N); R = np.zeros(N); t = np.arange(N) / SR
rng = np.random.default_rng(1990)
def put(at, y, g=1.0, pan=0.0):
    i = int(SR * at)
    if i >= N: return
    y = y[: N - i] * g; L[i:i + len(y)] += y * (1 - max(0, pan)); R[i:i + len(y)] += y * (1 + min(0, pan))
def bandnoise(n, center, width):
    x = rng.standard_normal(n); X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR)
    X *= np.exp(-((np.log(f + 1) - np.log(center)) ** 2) / width); y = np.fft.irfft(X, n); return y / (np.abs(y).max() + 1e-9)
def lowpass(y, fc):
    Y = np.fft.rfft(y); f = np.fft.rfftfreq(len(y), 1 / SR); Y *= 1 / (1 + (f / fc) ** 4); return np.fft.irfft(Y, len(y))
def env(n, a, d): u = np.arange(n) / SR; return (1 - np.exp(-u / a)) * np.exp(-u / d)
def reverb(y, decay=1.2, mix=.5):
    n = int(SR * decay * 1.5); ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR / (decay / 4)); ir /= np.abs(ir).sum() ** .5 * 6
    m = len(y) + n; out = np.fft.irfft(np.fft.rfft(y, m) * np.fft.rfft(ir, m), m)
    dry = np.zeros(m); dry[:len(y)] = y; return dry * (1 - mix) + out * mix
def seg(name): return S[name][0], S[name][1]
def window(a, b, ramp=1.0): return np.clip((t - a) / ramp, 0, 1) * np.clip((b - t) / ramp, 0, 1)
def step(g=.3, bright=1500, dur=.12):
    n = int(SR * dur); return lowpass(bandnoise(n, 380, .6), bright) * env(n, .002, .03) * g
def click(g, fc=4000): n = int(SR * .04); return bandnoise(n, fc, .3) * env(n, .0005, .006) * g

# ── 底噪：低频嗡 + 暗噪声；黑暗段更闷，结尾展厅更“空”
drone = .05 * np.sin(2 * np.pi * 55 * t) + .03 * np.sin(2 * np.pi * 82.4 * t + np.sin(t * .3))
room = lowpass(bandnoise(N, 180, 1.2), 900) * .035
inside = np.clip(1 - window(*seg("dark"), 2) * .5 - window(*seg("hours"), 2) * .4, 0, 1)
amb = (drone + room) * (.6 + .5 * inside); L += amb; R += amb
# 监控嗡声（值班台、离开桌子）
a, b = S["desk"][0], S["away"][1]
hum = (.012 * np.sin(2 * np.pi * 60 * t) + .006 * np.sin(2 * np.pi * 120 * t)) * window(a, b, .5); L += hum; R += hum
# ── 心跳
for k, bt in enumerate(ev["beats"]):
    n = int(SR * .3); u = np.arange(n) / SR
    tens = float(np.interp(bt, [0, 70, 110, 140, 200, 287, 297, 330, 345, 360, 392], [.08, .3, .7, 1, .8, .9, .45, .35, .6, .15, .1]))
    put(bt, np.sin(2 * np.pi * 52 * u * (1 - u * .8)) * env(n, .004, .07), (.2 + .55 * tens) * (1 if k % 2 == 0 else .7))
# ── 1 巡夜：自己的脚步 + 钥匙
for s in np.arange(1.0, 40, .56): put(float(s), reverb(step(.22), .9, .35), 1, .15 if int(s / .56) % 2 else -.15)
for s in np.arange(40, 55, 1.4): put(float(s), reverb(step(.16), .9, .35))
for s in [8, 23, 37]:
    for k in range(5): n = int(SR * .05); put(s + k * .045 + rng.random() * .02, bandnoise(n, 6000, .2) * env(n, .001, .015) * .12, 1, .3)
# ── 2 值班台：门铃两次、对讲机、开门按钮
d0 = S["desk"][0]
n = int(SR * .75); u = np.arange(n) / SR
buzz = lowpass(np.sign(np.sin(2 * np.pi * 330 * u)) * .5 + np.sign(np.sin(2 * np.pi * 495 * u)) * .25, 2500) * np.clip(u / .01, 0, 1) * np.clip((.75 - u) / .03, 0, 1)
put(d0 + 8, buzz, .16, .3); put(d0 + 12.5, buzz, .16, .3)
for s in [d0 + 13.8, d0 + 19.6]: n = int(SR * .5); put(s, bandnoise(n, 2500, .5) * env(n, .01, .2), .06)   # 对讲机的嘶声
put(d0 + 29.6, click(.5)); put(d0 + 29.7, click(.7, 1800), 1, -.2)
n = int(SR * 1.6); u = np.arange(n) / SR
creak = bandnoise(n, 700, .08) * (np.sin(2 * np.pi * (3 + 2 * u) * u) * .5 + .5) * env(n, .2, .8)
c0 = S["corridor"][0]; put(c0, click(.9, 900)); put(c0 + .05, reverb(creak, 1.4, .4), .18, -.1)
# ── 3 走廊：两人的脚步，越来越近，然后停下
for k, s in enumerate(np.arange(c0 + .7, c0 + 6.6, .3)): put(float(s), reverb(step(.12 + .5 * (s - c0) / 6), 1.2, .4), 1, .25 if k % 2 else -.25)
# ── 4 离开桌子：自己的两步，一个很轻的高音逐渐升起
w0 = S["away"][0]; put(w0 + 1.2, step(.35)); put(w0 + 2.6, step(.3))
n = int(SR * 14); u = np.arange(n) / SR; put(w0, np.sin(2 * np.pi * (880 + 40 * u) * u) * np.clip(u / 8, 0, 1) * np.clip((14 - u) / 1, 0, 1), .018)
# ── 5 面墙：转身呼啸、手铐、对讲机
wl = S["wall"][0]
n = int(SR * 1.3); u = np.arange(n) / SR; put(wl, bandnoise(n, 400, .5) * np.sin(np.pi * u / 1.3) ** 2, .22)
for k in range(6): n = int(SR * .025); put(wl + 2.2 + k * .028, bandnoise(n, 5200 - k * 250, .15) * env(n, .0003, .005), .8 - k * .1, .1)
n = int(SR * 2.4); u = np.arange(n) / SR; put(wl + 2.25, np.sin(2 * np.pi * 6200 * u) * np.exp(-u / 1.1) * np.clip(u / .05, 0, 1), .03)
n = int(SR * 7); u = np.arange(n) / SR
static = bandnoise(n, 2200, .6) * (.5 + .5 * np.abs(np.sin(u * 7))) * np.clip(u / .1, 0, 1) * np.clip((7 - u) / .3, 0, 1)
put(wl + 10.5, static, .07, -.4)
for s in [wl + 10.4, wl + 17.4]: n = int(SR * .12); put(s, np.sin(2 * np.pi * 1400 * np.arange(n) / SR) * env(n, .002, .05), .08, -.4)
# ── 6 下楼梯：三个人的脚步，带回声；最后一扇铁门
s0 = S["stairs"][0]
for k, s in enumerate(np.arange(s0 + .4, s0 + 22, .62)): put(float(s), reverb(step(.3, 1200, .15), 2.0, .6), 1, (k % 3 - 1) * .3)
n = int(SR * .5); put(s0 + 23.5, reverb(lowpass(bandnoise(n, 160, .6), 600) * env(n, .003, .12), 2.2, .5), .6)
# ── 7 胶带：三下撕扯
tp = S["tape"][0]
for k in range(3):
    n = int(SR * .55); u = np.arange(n) / SR
    rip = bandnoise(n, 2600, .9) * (.6 + .4 * np.sign(np.sin(2 * np.pi * 38 * u))) * env(n, .01, .25)
    put(tp + 1 + k * 1.8, rip, .5, (k - 1) * .3)
# ── 8 黑暗：楼上的脚步、玻璃碎、刮擦（都闷、都远）
dk0, dk1 = S["dark"]
for s in np.arange(dk0 + 3, dk1 - 2, .7):
    if rng.random() < .55: put(float(s), lowpass(step(.5, 400), 300), .5, rng.uniform(-.5, .5))
for lt0 in ev["loss"]:
    n = int(SR * .6); smash = bandnoise(n, 3500, 1.2) * env(n, .001, .12)
    put(lt0 + 1, reverb(lowpass(smash, 2200), 1.8, .6), .45, rng.uniform(-.4, .4))
    n = int(SR * 2.4); u = np.arange(n) / SR
    scrape = bandnoise(n, 1600, .5) * (.4 + .6 * np.abs(np.sin(2 * np.pi * 3.3 * u))) * np.clip(u / .2, 0, 1) * np.clip((2.4 - u) / .3, 0, 1)
    put(lt0 + 2, lowpass(scrape, 1800), .09, rng.uniform(-.3, .3))
# ── 10 漫长的几个小时：滴水；清晨远处的车声慢慢升起
h0, h1 = S["hours"]
for s in np.arange(h0 + .5, h1, 1.11):
    n = int(SR * .25); u = np.arange(n) / SR; put(float(s), reverb(np.sin(2 * np.pi * (1800 - 900 * u) * u) * env(n, .001, .03), 1.5, .5), .08, -.3)
traffic = lowpass(bandnoise(N, 120, 1.0), 400) * .04 * np.clip((t - (h0 + 12)) / 15, 0, 1) * np.clip((S["frames"][0] - t) / 2, 0, 1)
L += traffic; R += traffic
# ── 11 早晨：闷闷的人声、门、急促脚步、撕胶带
m0 = S["morning"][0]
n = int(SR * 18); u = np.arange(n) / SR
babble = sum(bandnoise(n, f, .25) * (.5 + .5 * np.sin(2 * np.pi * r * u + ph)) ** 2 for f, r, ph in [(420, 3.1, 0), (650, 4.3, 1), (900, 2.7, 2)])
babble = lowpass(babble, 1200) * np.clip(u / 1.5, 0, 1) * np.clip((18 - u) / 2, 0, 1) * (0.5 + .5 * np.clip((u - 7) / 2, 0, 1))
put(m0 + 1, babble, .06)
n = int(SR * .5); put(m0 + 4, reverb(lowpass(bandnoise(n, 200, .6), 700) * env(n, .003, .1), 1.6, .4), .5)
for s in np.arange(m0 + 4.5, m0 + 6.8, .28): put(float(s), reverb(step(.35), 1.2, .3))
n = int(SR * .8); u = np.arange(n) / SR; put(m0 + 7, bandnoise(n, 2800, .9) * (.6 + .4 * np.sign(np.sin(2 * np.pi * 45 * u))) * env(n, .005, .3), .7)
# ── 12 空画框：安静的展厅，一个长长的低音
f0 = S["frames"][0]
n = int(SR * (END - f0)); u = np.arange(n) / SR
tone = (np.sin(2 * np.pi * 110 * u) * .6 + np.sin(2 * np.pi * 164.8 * u) * .3 + np.sin(2 * np.pi * 220 * u) * .1) * np.clip(u / 6, 0, 1) * np.clip((END - f0 - u) / 6, 0, 1)
put(f0, tone, .05)
# 收尾
fo = np.clip((END - t) / 1.5, 0, 1) * np.clip(t / .8, 0, 1); L *= fo; R *= fo
st = np.stack([L, R], 1); st /= max(1e-9, np.abs(st).max()) / .89
with wave.open("sound_full.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())
print("sound ok", END, "s")
