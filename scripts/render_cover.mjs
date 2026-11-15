#!/usr/bin/env node
// 把封面 HTML 渲染成公众号一图流封面：设计稿 1283×383，3 倍导出 3849×1149 的 JPG。
// 为什么必须 3x：手机是 3 倍屏，横版区实际显示宽约 1100 像素，1x 会被微信拉伸 + 再压一道 JPEG，双重损失就糊了。
// 用法：node render_cover.mjs <封面.html> <输出.jpg>
// 依赖：npm i puppeteer-core，本机装有 Chrome / Chromium / Edge（或设置环境变量 CHROME_PATH）
import fs from 'node:fs';
import path from 'node:path';
import puppeteer from 'puppeteer-core';

const [, , htmlArg, outArg] = process.argv;
if (!htmlArg || !outArg) { console.error('用法：node render_cover.mjs <封面.html> <输出.jpg>'); process.exit(1); }

const candidates = [
  process.env.CHROME_PATH,
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
  '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
].filter(Boolean);
const executablePath = candidates.find(p => fs.existsSync(p));
if (!executablePath) { console.error('没找到 Chrome，请设置 CHROME_PATH'); process.exit(1); }

const browser = await puppeteer.launch({ executablePath, headless: 'new',
  args: ['--hide-scrollbars', '--font-render-hinting=none'] });
const page = await browser.newPage();
await page.setViewport({ width: 1283, height: 383, deviceScaleFactor: 3 }); // ← 3x，别改回 1x
await page.goto('file://' + path.resolve(htmlArg), { waitUntil: 'networkidle0' });
await page.evaluate(() => document.fonts.ready);
await (await page.$('.wrap')).screenshot({ path: path.resolve(outArg), type: 'jpeg', quality: 90 });
await browser.close();
console.log('→', path.resolve(outArg), '（应为 3849×1149）');
