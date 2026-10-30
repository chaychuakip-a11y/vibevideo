// 逐帧渲染：node render.js [fps] [只出这些秒的静帧...]
const { chromium } = require("playwright");
const fs = require("fs"), path = require("path");
const FPS = +(process.argv[2] || 60), END = 14;
const stills = process.argv.slice(3).map(Number);
const out = path.join(__dirname, stills.length ? "stills" : "frames");
fs.mkdirSync(out, { recursive: true });

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto("file://" + path.join(__dirname, "sample_14s.html"));
  await page.evaluate(() => window.ready);
  const times = stills.length ? stills : [...Array(Math.round(END * FPS)).keys()].map(i => i / FPS);
  for (let i = 0; i < times.length; i++) {
    await page.evaluate(t => window.draw(t), times[i]);
    const name = stills.length ? `t${times[i].toFixed(2)}.jpg` : `f${String(i).padStart(5, "0")}.jpg`;
    await page.locator("canvas").screenshot({ path: path.join(out, name), type: "jpeg", quality: 95 });
    if (i % 120 === 0) console.log(i, "/", times.length);
  }
  await browser.close();
})();
