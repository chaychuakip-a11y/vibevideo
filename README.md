# Vibe知识大赏 · 代码生成知识短片

用代码逐帧渲染的中文知识短片（vibe-knowledge skill，基础档 0 积分）。每个文件夹里有：

- `film.html` —— 整部片子：一个 canvas + `draw(t)` 函数，脚本表（字幕、关键词、出处、动画节点）在文件开头
- `render.js` —— 用 Playwright 逐帧截取 canvas，输出 JPEG 帧
- `sfx.py` —— 用 numpy 合成的代码音效
- `post.txt` —— 中文发布文案（标题、简介、话题、出处）
- `*.mp4` —— 成片（小于 100 MB 的版本）

| 文件夹 | 片名 | 时长 | 风格 |
|---|---|---|---|
| `yawning/` | 哈欠为什么会传染 | 2:34（另有 14 秒样片） | 深色数学（Dark Math） |
| `battery/` | 手机电量 20% 为什么会关机 | 2:38 | 深色数学 |
| `coin-debasement/` | 钱是怎么被动手脚的 · 第〇集 | 5:05（另有 15 秒样片） | 水墨纸本 |
| `queue/` | 为什么你排的队总是最慢 | 10:51 | 象形统计（ISOTYPE） |
| `water/` | 古代城市怎么喝上水 | 10:14 | 蓝图专利图（Blueprint） |
| `heist/` | 守夜人：1990 加德纳博物馆失窃案（第一视角实验短片） | 6:32（另有 14 秒样片） | 暗调抽象第一视角 |

## 重新渲染

```bash
cd queue
NODE_PATH=$(npm root -g) node render.js 30        # 逐帧渲染到 frames/，同时写出 events.json
python3 sfx.py                                    # 读 events.json 合成音效 sfx.wav
python3 ~/.claude/skills/vibe-knowledge/tools/fit_bgm.py bgm.wav --seconds <片长>   # 默认 BGM 按片长裁剪
# 再用 ffmpeg 把 frames/ + bgm.wav + sfx.wav 合成 MP4（参数见 encode.sh）
```

需要：Node + Playwright（Chromium）、Python 3 + numpy、ffmpeg、能访问 Google Fonts 的网络，以及 vibe-knowledge skill 里的默认 BGM。

## 说明

- 帧图片（每部 2–4 GB）和 380 MB 的 1080p60 原版未放入仓库；哈欠、电池两部放的是压缩后的 1080p60 与 720p 版本，可以用上面的步骤重新渲染出原画质。
- 视频中标注「示意」的数字、曲线和模拟仅用于说明，出处见各片 `post.txt` 和画面左下角脚注。
