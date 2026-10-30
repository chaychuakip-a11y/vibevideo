// 逐帧渲染：node render.js <fps> [静帧秒...]
// 直接从 canvas 取 JPEG（比截图快），多个页面并行，支持断点续渲
const { chromium } = require("playwright");
const fs = require("fs"), path = require("path"), os = require("os");
const FPS = +(process.argv[2] || 60);
const stills = process.argv.slice(3).map(Number);
const out = path.join(__dirname, stills.length ? "stills" : "frames");
fs.mkdirSync(out, { recursive: true });

(async () => {
  const browser = await chromium.launch();
  const open = async () => {
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
    await page.goto("file://" + path.join(__dirname, "sample_14s.html"));
    await page.evaluate(() => window.ready);
    return page;
  };
  const first = await open();
  const END = await first.evaluate(() => window.END);
  fs.writeFileSync(path.join(__dirname, "events.json"), JSON.stringify(await first.evaluate(() => window.events())));
  const jobs = stills.length
    ? stills.map(t => [t, `t${t.toFixed(2).padStart(6, "0")}.jpg`])
    : [...Array(Math.round(END * FPS)).keys()].map(i => [i / FPS, `f${String(i).padStart(5, "0")}.jpg`])
        .filter(([, n]) => !fs.existsSync(path.join(out, n)));
  const N = Math.max(1, Math.min(4, os.cpus().length - 1));
  const pages = [first, ...await Promise.all([...Array(N - 1)].map(open))];
  let next = 0, done = 0;
  await Promise.all(pages.map(async page => {
    while (next < jobs.length) {
      const [t, name] = jobs[next++];
      const b64 = await page.evaluate(t => { window.draw(t); return document.getElementById("c").toDataURL("image/jpeg", .95).slice(23); }, t);
      fs.writeFileSync(path.join(out, name), Buffer.from(b64, "base64"));
      if (++done % 600 === 0) console.log(done, "/", jobs.length);
    }
  }));
  await browser.close();
  console.log("done", jobs.length);
})();
