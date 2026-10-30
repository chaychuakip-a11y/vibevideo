// 逐帧渲染 full.html：node render_full.js <fps> [静帧秒...]
// 全片模式按帧号分给多个页面并行，另外导出哈欠事件表 yawns.json 给音效用
const { chromium } = require("playwright");
const fs = require("fs"), path = require("path"), os = require("os");
const FPS = +(process.argv[2] || 60);
const stills = process.argv.slice(3).map(Number);
const out = path.join(__dirname, stills.length ? "stills_full" : "frames_full");
fs.mkdirSync(out, { recursive: true });

(async () => {
  const browser = await chromium.launch();
  const open = async () => {
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
    await page.goto("file://" + path.join(__dirname, "film.html"));
    await page.evaluate(() => window.ready);
    return page;
  };
  const first = await open();
  const END = await first.evaluate(() => window.END);
  fs.writeFileSync(path.join(__dirname, "yawns.json"), JSON.stringify(await first.evaluate(() => window.yawns())));
  const jobs = stills.length
    ? stills.map(t => [t, `t${t.toFixed(2).padStart(6, "0")}.jpg`])
    : [...Array(Math.round(END * FPS)).keys()].map(i => [i / FPS, `f${String(i).padStart(5, "0")}.jpg`])
        .filter(([, n]) => !fs.existsSync(path.join(out, n)));   // 断点续渲
  const N = Math.max(1, Math.min(6, os.cpus().length - 1));
  const pages = [first, ...await Promise.all([...Array(N - 1)].map(open))];
  let next = 0, done = 0;
  await Promise.all(pages.map(async page => {
    while (next < jobs.length) {
      const [t, name] = jobs[next++];
      await page.evaluate(t => window.draw(t), t);
      await page.locator("canvas").screenshot({ path: path.join(out, name), type: "jpeg", quality: 95 });
      if (++done % 600 === 0) console.log(done, "/", jobs.length);
    }
  }));
  await browser.close();
  console.log("done", jobs.length);
})();
