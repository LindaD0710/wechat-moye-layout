# wechat-moye-layout · 公众号排版流水线

把公众号排版从 2 小时压到 10 分钟：**定死规范 → 封面改两行字出图 → 正文一键生成、整页复制粘贴。**

这是一个 Agent Skill（Claude Code / Codex 等都能用），也可以脱离 AI 直接跑脚本。

## 包含什么
| 文件 | 作用 |
|---|---|
| `SKILL.md` | 给 AI 读的流程说明 |
| `assets/cover-template.html` | 一图流封面模板（1283×383，左横版右方形） |
| `scripts/render_cover.mjs` | 3 倍导出封面 → 3849×1149 JPG |
| `scripts/build_wx.py` | Markdown → 全内联样式 HTML，图片内嵌，可直接粘进公众号编辑器 |
| `references/visual-spec.md` | 墨夜视觉规范（颜色、字体、尺寸） |
| `references/prompt-for-ai.md` | 不会代码的人，可以直接发给 AI 的一段话 |

## 快速开始
```bash
npm i                                   # 安装 puppeteer-core（需要本机有 Chrome）
# 字体：下载思源宋体 Heavy 放到 fonts/SourceHanSerifSC-Heavy.otf（或装到系统）

node scripts/render_cover.mjs assets/cover-template.html cover.jpg
python3 scripts/build_wx.py examples/sample.md sample.html "示例" "# 示例：排版这件重复活，我用 AI 做掉了"
open sample.html                        # 全选 → 复制 → 粘进公众号编辑器
```

## 作为 Skill 安装
把整个文件夹放进你的 skills 目录（如 `~/.claude/skills/` 或项目的 `.agents/skills/`）。

## 作者
琳达 · AI + 营销。营销里那些天天都会遇到的真问题，都值得用 AI 重新做一遍。
