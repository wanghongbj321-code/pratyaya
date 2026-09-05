#!/usr/bin/env node
/**
 * canvas-smoke.mjs —— 分级渲染验收 L2 DOM 度量断言（可选增强 + 降级路径）
 *
 * 用法：
 *   node skills/canvas-render/scripts/canvas-smoke.mjs <html> --type <canvas_type>
 *   [--chrome <chrome-path>] [--viewport 1440x900,390x844] [--json]
 *
 * 定位：
 *   - `audit_canvas_html.py` 是 Python 标准库零依赖、可随 skill 分发的 L1 静态审计；
 *     本脚本依赖 puppeteer-core（随装不含 node_modules）+ 本机 Chrome，跨机器不可移植，
 *     因此仅作 L2 的"脚本可用时执行"。执行前先环境自检（puppeteer-core 可 resolve +
 *     Chrome 路径存在），任一缺失则打印降级原因并以 exit code 2 退出（不阻断交付、
 *     不新增下载；调用方应在渲染自检中记录降级原因并改走 L3 截图路径）。
 *   - 断点期望 / 结构签名 / 滚动豁免均从 CANVAS_TYPE_BREAKPOINTS 表读取，不硬编码
 *     单一 canvas_type 的选择器。
 *
 * 断言内容（L2）：
 *   ① 无横向溢出：documentElement.scrollWidth <= innerWidth
 *   ② 文本裁切按容器类型分类断言：无内部滚动意图的文本容器
 *      scrollHeight <= clientHeight + 2；设计预期内滚动的容器（豁免清单）跳过，
 *      只断言其滚动区不溢出父容器（由全局 hOverflow 兜底）
 *   ③ 结构签名断言：该 canvas_type 的签名布局存在且数量正确（按配置表）
 *   ④ 打印仿真（可选，--print）：emulateMediaType('print') 下断言无打印专属横向溢出
 *
 * 退出码：0 = PASS；1 = FAIL；2 = DEGRADED（依赖/环境缺失，降级走 L3）
 */

import { createRequire } from "node:module";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/* ------------------------------------------------------------------ *
 * 0. 配置表：按 canvas_type 声明断点期望 / 结构签名 / 滚动豁免
 *    （表驱动，脚本逻辑不硬编码单一画布选择器；新增画布在此追加）
 * ------------------------------------------------------------------ */
const DEFAULT_VIEWPORTS = [
  [1440, 900],
  [390, 844],
];

/**
 * 每类画布：
 * - clipTargets: 参与"文本裁切分类断言"的候选容器选择器
 * - scrollable:  豁免清单——设计预期内滚动的容器（其滚动区不溢出父容器即视为正常，
 *                由全局 hOverflow 兜底，不做 scrollHeight<=clientHeight 断言）
 * - signatures:  结构签名断言（存在且数量正确），在每个视口下都校验 DOM 数量
 */
const CANVAS_TYPE_BREAKPOINTS = {
  mvl: {
    clipTargets: ["section", "article", ".maau-card", ".board", ".validation-box", ".governance-item"],
    scrollable: [".bpmn-flow-wrap", ".maau-flow", "[data-scroll-x]", ".scroll-x"],
    signatures: [
      { name: "MVL Workflow 根锚点", selector: "#workflow-flow", count: 1 },
      { name: "MVL Workflow SVG", selector: ".bpmn-flow", min: 1 },
      { name: "MVL Workflow 轨道带", selector: ".bpmn-track", min: 1 },
      { name: "MVL Workflow 图例", selector: ".bpmn-legend", count: 1 },
      { name: "治理面板", selector: "#quality-panel", count: 1 },
    ],
  },
  "5w": {
    clipTargets: ["section", "article", ".card", ".why-row", "table", "th", "td", ".col"],
    scrollable: [".chain .why-link", ".workflow-flow", "[data-scroll-x]", ".scroll-x"],
    signatures: [
      { name: "5W 五层 Why 卡片", selector: ".why-row", count: 5 },
      { name: "对策四列（DOM 数不随折叠变化）", selector: ".grid4 .col", count: 4 },
      { name: "治理面板", selector: "#quality-panel", count: 1 },
    ],
    // 断点折叠期望（vp 键 = 视口 `WxH`，只校验实际运行的视口；不存在的键自动跳过）
    breakpoints: [
      { vp: "1440x900", selector: ".chain", prop: "flexDirection", expect: "row", name: ".chain 桌面横向并排" },
      { vp: "1440x900", selector: ".grid4", prop: "gridTracks", expect: 4, name: ".grid4 桌面四列" },
      { vp: "390x844", selector: ".chain", prop: "flexDirection", expect: "column", name: ".chain ≤1180px 纵向回退" },
      { vp: "390x844", selector: ".grid4", prop: "gridTracks", expect: 1, name: ".grid4 ≤720px 单列" },
    ],
  },
  // 其余 canvas_type 暂未登记结构签名 / 断点表：仍跑通用无溢出/无裁切断言；
  // 需要结构签名与断点折叠时按同样字段追加（eg golden-circle 三圈 / v2c-vac 归因链）。
};

/* ------------------------------------------------------------------ *
 * 1. 环境自检：puppeteer-core resolve + Chrome 路径
 * ------------------------------------------------------------------ */
function findPuppeteerCore() {
  // 1) 环境变量显式指定
  if (process.env.PUPPETEER_CORE_PATH && fs.existsSync(process.env.PUPPETEER_CORE_PATH)) {
    return process.env.PUPPETEER_CORE_PATH;
  }
  // 2) 从脚本向上 require.resolve（脚本同目录若存在 node_modules 时命中）
  try {
    const req = createRequire(import.meta.url);
    return req.resolve("puppeteer-core");
  } catch {
    /* 继续候选路径 */
  }
  // 3) managed node workspace 常见路径（随装不含 node_modules，逐台机器探测）
  const home = os.homedir();
  const candidates = [
    path.join(home, ".workbuddy", "binaries", "node", "workspace", "node_modules", "puppeteer-core"),
    path.join(home, ".codebuddy", "binaries", "node", "workspace", "node_modules", "puppeteer-core"),
    path.join(home, ".workbuddy", "plugins", "cache", "node", "workspace", "node_modules", "puppeteer-core"),
    path.join(home, ".codebuddy", "plugins", "cache", "node", "workspace", "node_modules", "puppeteer-core"),
  ];
  for (const c of candidates) {
    if (fs.existsSync(c)) return c;
  }
  return null;
}

const DEFAULT_CHROME_PATHS = [
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/usr/bin/google-chrome",
  "/usr/bin/google-chrome-stable",
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
];

function findChrome(explicit) {
  if (explicit && fs.existsSync(explicit)) return explicit;
  if (process.env.CHROME_PATH && fs.existsSync(process.env.CHROME_PATH)) return process.env.CHROME_PATH;
  for (const c of DEFAULT_CHROME_PATHS) if (fs.existsSync(c)) return c;
  return null;
}

function parseArgs(argv) {
  const args = { html: null, type: null, chrome: null, json: false, print: false, viewports: DEFAULT_VIEWPORTS };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--type") args.type = argv[++i];
    else if (a === "--chrome") args.chrome = argv[++i];
    else if (a === "--viewport") args.viewports = argv[++i].split(";").map((s) => s.split("x").map(Number));
    else if (a === "--json") args.json = true;
    else if (a === "--print") args.print = true;
    else if (!a.startsWith("--")) args.html = a;
  }
  return args;
}

/* ------------------------------------------------------------------ *
 * 2. 页面断言
 * ------------------------------------------------------------------ */
async function measureViewport(page, viewport, cfg, withPrint) {
  const [width, height] = viewport;
  await page.setViewport({ width, height });

  // 过滤出适用于当前视口的断点规则（按 vp 键 `WxH` 精确匹配）
  const vpKey = `${width}x${height}`;
  const activeBreakpoints = (cfg.breakpoints || []).filter((b) => b.vp === vpKey);

  const r = await page.evaluate(
    ({ clipTargets, scrollable, signatures, breakpoints, vp }) => {
      const out = {
        hOverflow: false,
        clips: [],
        signatureFailures: [],
        breakpointFailures: [],
        vp,
      };
      out.hOverflow = document.documentElement.scrollWidth > window.innerWidth;

      // ① 断点折叠断言
      for (const bp of breakpoints) {
        const el = document.querySelector(bp.selector);
        if (!el) {
          out.breakpointFailures.push({ name: bp.name, selector: bp.selector, reason: "selector 不存在" });
          continue;
        }
        const cs = getComputedStyle(el);
        if (bp.prop === "gridTracks") {
          const tracks = cs.gridTemplateColumns.split(" ").filter(Boolean).length;
          if (tracks !== bp.expect) {
            out.breakpointFailures.push({ name: bp.name, selector: bp.selector, expected: bp.expect, actual: tracks });
          }
        } else {
          const actual = cs[bp.prop];
          if (actual !== bp.expect) {
            out.breakpointFailures.push({ name: bp.name, selector: bp.selector, expected: bp.expect, actual });
          }
        }
      }

      // ② 文本裁切分类断言：非豁免文本容器 scrollHeight <= clientHeight + 2
      if (Array.isArray(clipTargets) && clipTargets.length > 0) {
        const sel = clipTargets.join(",");
        for (const el of document.querySelectorAll(sel)) {
          const cs = getComputedStyle(el);
          if (cs.display === "none" || cs.visibility === "hidden") continue;
          const isScrollable = Array.isArray(scrollable) && scrollable.some((s) => el.closest(s));
          if (isScrollable) continue; // 设计内滚动容器：豁免内部裁切断言，由全局 hOverflow 兜底
          if (el.clientHeight === 0) continue; // 空/不可度量容器跳过
          if (el.scrollHeight > el.clientHeight + 2) {
            out.clips.push({
              tag: el.tagName.toLowerCase(),
              cls: (el.className && String(el.className).slice(0, 80)) || "",
              id: el.id || "",
              scrollHeight: el.scrollHeight,
              clientHeight: el.clientHeight,
            });
          }
        }
      }

      // ③ 结构签名断言
      if (Array.isArray(signatures)) {
        for (const s of signatures) {
          const actual = document.querySelectorAll(s.selector).length;
          if (Number.isInteger(s.count) && actual !== s.count) {
            out.signatureFailures.push({ name: s.name, selector: s.selector, expected: s.count, actual });
          } else if (Number.isInteger(s.min) && actual < s.min) {
            out.signatureFailures.push({ name: s.name, selector: s.selector, expected: `>=${s.min}`, actual });
          } else if (Number.isInteger(s.max) && actual > s.max) {
            out.signatureFailures.push({ name: s.name, selector: s.selector, expected: `<=${s.max}`, actual });
          }
        }
      }
      return out;
    },
    {
      clipTargets: cfg.clipTargets || [],
      scrollable: cfg.scrollable || [],
      signatures: cfg.signatures || [],
      breakpoints: activeBreakpoints,
      vp: vpKey,
    },
  );

  let printHOverflow = null;
  if (withPrint) {
    await page.emulateMediaType("print");
    printHOverflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
    await page.emulateMediaType(null);
  }

  return { viewport: `${width}x${height}`, ...r, printHOverflow };
}

/* ------------------------------------------------------------------ *
 * 3. main
 * ------------------------------------------------------------------ */
async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (!args.html || !args.type) {
    console.error(
      "用法: node canvas-smoke.mjs <html> --type <canvas_type> [--chrome <path>] [--print] [--json]",
    );
    return 1;
  }

  // 环境自检（降级不阻断交付）
  const puppeteerCorePath = findPuppeteerCore();
  const chromePath = findChrome(args.chrome);
  if (!puppeteerCorePath || !chromePath) {
    const reason = [
      !puppeteerCorePath ? "puppeteer-core 不可 resolve" : null,
      !chromePath ? "未找到本机 Chrome（可传 --chrome 或设 CHROME_PATH）" : null,
    ]
      .filter(Boolean)
      .join("；");
    if (args.json) {
      console.log(JSON.stringify({ status: "DEGRADED", reason }, null, 2));
    } else {
      console.log(`[canvas-smoke] DEGRADED — ${reason}。不阻断交付：请改走 L3 截图路径，并在渲染自检中记录降级原因。`);
    }
    return 2;
  }

  const cfg = CANVAS_TYPE_BREAKPOINTS[args.type] || {};
  const htmlAbs = path.resolve(args.html);
  if (!fs.existsSync(htmlAbs)) {
    console.error(`[canvas-smoke] FAIL — HTML 不存在: ${htmlAbs}`);
    return 1;
  }

  const req = createRequire(pathToFileURL(path.join(__dirname, "resolver.cjs")).href);
  let puppeteer;
  try {
    puppeteer = req(puppeteerCorePath);
  } catch (e) {
    const reason = `puppeteer-core 加载失败: ${e.message.split("\n")[0]}`;
    if (args.json) console.log(JSON.stringify({ status: "DEGRADED", reason }, null, 2));
    else console.log(`[canvas-smoke] DEGRADED — ${reason}。不阻断交付：请改走 L3 截图路径，并在渲染自检中记录降级原因。`);
    return 2;
  }

  const browser = await puppeteer.launch({
    executablePath: chromePath,
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu", "--hide-scrollbars"],
  });

  const results = [];
  try {
    const page = await browser.newPage();
    await page.goto(pathToFileURL(htmlAbs).href, { waitUntil: "networkidle0", timeout: 30000 });
    for (const vp of args.viewports) {
      results.push(await measureViewport(page, vp, cfg, args.print));
    }
  } finally {
    await browser.close();
  }

  const failed = results.filter(
    (r) =>
      r.hOverflow ||
      r.clips.length > 0 ||
      r.signatureFailures.length > 0 ||
      r.breakpointFailures.length > 0 ||
      (args.print && r.printHOverflow),
  );
  const status = failed.length === 0 ? "PASS" : "FAIL";

  if (args.json) {
    console.log(JSON.stringify({ status, results }, null, 2));
  } else {
    for (const r of results) {
      const flags = [];
      if (r.hOverflow) flags.push("横向溢出");
      if (r.clips.length) flags.push(`文本裁切×${r.clips.length}`);
      if (r.signatureFailures.length) {
        flags.push(r.signatureFailures.map((f) => `${f.name} ${f.actual}/${f.expected}`).join("、"));
      }
      if (r.breakpointFailures.length) {
        flags.push(
          r.breakpointFailures.map((f) => `${f.name}${f.reason ? "(" + f.reason + ")" : ""}`).join("、"),
        );
      }
      if (args.print && r.printHOverflow) flags.push("打印仿真横向溢出");
      console.log(`[canvas-smoke] ${r.viewport} — ${flags.length ? "FAIL: " + flags.join(" | ") : "PASS"}`);
    }
  }
  return failed.length === 0 ? 0 : 1;
}

main().then((code) => process.exit(code));
