#!/usr/bin/env python3
"""把 Markdown 文章转成可整页复制粘贴进公众号编辑器的 HTML（全内联样式，图片转 base64）。

用法：
  python3 build_wx.py 文章.md 输出.html "文章标题" "正文起始标记" \
      [--accent "#D8FF00"] [--hilite "#D8FF00"] [--note "脚注"] \
      [--divider-before "结尾自我介绍那一段的原文"] [--stop-at "## 事实核查备忘"]

支持的 Markdown：
  ### 小标题      → 自动编号小方块（01、02…）+ 居中粗体标题
  > 引用          → 墨夜黑底金句卡（卡内加粗走奶油白粗体，不压荧光笔）
  **重点**        → 荧光笔（话题色底 + 墨夜黑字），全文建议只用 5–6 处
  ![图注](路径)   → 图片（转 base64 内嵌）+ 灰色小字图注
  | 表格 |        → 表头墨夜黑底，斑马纹
  - 列表        → 圆点列表（列表内加粗走普通粗体，不占荧光笔配额）
  ``` 代码块 ```  → 浅色提示词框（适合放"可以直接复制给 AI 的话术"）
  `行内代码`
"""
import argparse, base64, html, mimetypes, os, pathlib, re

INK, CREAM, BODY = "#221A12", "#FBF4E6", "#3f3f3f"

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("src"); ap.add_argument("out"); ap.add_argument("title")
ap.add_argument("marker", help="正文从这一行之后开始，通常写文章的一级标题行")
ap.add_argument("note_pos", nargs="?", default="", help=argparse.SUPPRESS)      # 兼容旧版第 5 个位置参数
ap.add_argument("accent_pos", nargs="?", default=None, help=argparse.SUPPRESS)  # 兼容旧版第 6 个
ap.add_argument("hilite_pos", nargs="?", default=None, help=argparse.SUPPRESS)  # 兼容旧版第 7 个
ap.add_argument("--note", default=None, help="文末小字脚注，不传就不出")
ap.add_argument("--accent", default=None, help="章节编号数字色 + 引用块左边线，默认酸绿 #D8FF00")
ap.add_argument("--hilite", default=None, help="荧光笔底色，必须能压住墨夜黑字，默认同 accent")
ap.add_argument("--divider-before", default="我是琳达，深耕 AI+营销方向，一个会写 coding、会搭 AI Agent 的 Marketer。营销里那些天天都会遇到的真问题，都值得用 AI 重新做一遍。",
                help="在这一段之前插入 · · · 分隔符（结尾三件套），传空字符串关闭")
ap.add_argument("--stop-at", default="## 事实核查备忘", help="遇到这一行就截断，后面的备忘不进排版")
a = ap.parse_args()

NOTE_TEXT = a.note if a.note is not None else a.note_pos
ACCENT = a.accent or a.accent_pos or "#D8FF00"
HILITE = a.hilite or a.hilite_pos or ACCENT

P    = f'<p style="margin:0 0 22px;font-size:15px;color:{BODY};line-height:1.85;letter-spacing:0.5px;">{{}}</p>'
NUM  = ('<p style="margin:44px 0 10px;text-align:center;"><span style="display:inline-block;'
        f'background:{INK};color:{ACCENT};font-size:15px;font-weight:bold;letter-spacing:4px;'
        'padding:5px 16px;border-radius:4px;">{}</span></p>')
HEAD = (f'<p style="margin:0 0 28px;text-align:center;font-size:18px;color:{INK};'
        'font-weight:bold;letter-spacing:1px;">{}</p>')
QUOTE= (f'<blockquote style="margin:0 0 22px;padding:16px 20px;background:{INK};'
        f'border-left:4px solid {ACCENT};border-radius:0 8px 8px 0;"><p style="margin:0;'
        f'font-size:15px;color:{CREAM};line-height:1.8;letter-spacing:0.5px;font-weight:bold;">'
        '{}</p></blockquote>')
MARK = f'<strong style="background:{HILITE};color:{INK};padding:1px 6px;border-radius:4px;">{{}}</strong>'
DIV  = '<p style="margin:40px 0;text-align:center;color:#cccccc;font-size:13px;letter-spacing:8px;">· · ·</p>'

md = pathlib.Path(a.src).read_text(encoding="utf-8")
if a.marker not in md:
    raise SystemExit(f"找不到正文起始标记：{a.marker}")
body = md.split(a.marker, 1)[1]
if a.stop_at:
    body = body.split(a.stop_at)[0]
body = body.rstrip().rstrip("-").rstrip()

def inline_plain(s):
    # 引用块是墨夜黑底，荧光笔贴上去会打架，这里只做奶油白粗体
    s = html.escape(s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)

def inline(s):
    s = html.escape(s)
    s = re.sub(r'`([^`]+)`', r'<code style="background:#f3f3f3;padding:1px 5px;border-radius:3px;font-size:14px;">\1</code>', s)
    return re.sub(r'\*\*(.+?)\*\*', lambda m: MARK.format(m.group(1)), s)

out, n, i = [], 0, 0
lines = body.split("\n")
while i < len(lines):
    ln = lines[i].rstrip()
    if not ln:
        i += 1; continue
    m_img = re.match(r'^!\[(.*?)\]\((.+?)\)\s*$', ln)
    if m_img:
        cap, src = m_img.group(1), m_img.group(2)
        if not os.path.isabs(src):
            src = os.path.join(os.path.dirname(a.src), src)
        mime = mimetypes.guess_type(src)[0] or "image/png"
        b64 = base64.b64encode(open(src, "rb").read()).decode()
        out.append(f'<p style="margin:26px 0 8px;"><img src="data:{mime};base64,{b64}" '
                   'style="width:100%;display:block;border-radius:6px;"></p>')
        if cap:
            out.append(f'<p style="margin:0 0 26px;text-align:center;font-size:12px;color:#999999;">{html.escape(cap)}</p>')
        i += 1; continue
    if ln.startswith("```"):
        i += 1; buf = []
        while i < len(lines) and not lines[i].startswith("```"):
            buf.append(lines[i]); i += 1
        i += 1
        inner = "<br>".join(html.escape(x) for x in buf if x.strip())
        out.append('<p style="margin:0 0 22px;padding:18px 20px;background:#faf8f3;'
                   f'border:1px solid #e6e0d5;border-radius:8px;font-size:14px;color:{INK};'
                   f'line-height:2.0;letter-spacing:0.5px;">{inner}</p>')
        continue
    if ln.startswith("- "):
        # 列表：列表里的加粗只做普通粗体，不占荧光笔配额
        items = []
        while i < len(lines) and lines[i].startswith("- "):
            items.append(lines[i][2:].rstrip()); i += 1
        lis = "".join(f'<li style="margin:0 0 10px;">{inline_plain(t)}</li>' for t in items)
        out.append(f'<ul style="margin:0 0 22px;padding-left:22px;font-size:15px;color:{BODY};line-height:1.85;letter-spacing:0.5px;">{lis}</ul>')
        continue
    if ln.startswith("### "):
        n += 1
        out.append(NUM.format(f"{n:02d}"))
        out.append(HEAD.format(inline(ln[4:])))
    elif ln.startswith("> "):
        out.append(QUOTE.format(inline_plain(ln[2:])))
    elif ln.startswith("|"):
        rows = []
        while i < len(lines) and lines[i].startswith("|"):
            rows.append(lines[i]); i += 1
        cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows if not set(r) <= set("|-: ")]
        tbl = [f'<table style="width:100%;border-collapse:collapse;margin:0 0 22px;font-size:14px;color:{BODY};">']
        for r_i, r in enumerate(cells):
            bg = INK if r_i == 0 else ("#ffffff" if r_i % 2 else "#faf8f3")
            col = ACCENT if r_i == 0 else BODY
            w = "bold" if r_i == 0 else "normal"
            def cell(c):
                # 表格里的加粗只做普通粗体，荧光笔留给正文重点句
                txt = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html.escape(c))
                return (f'<td style="padding:10px 12px;border:1px solid #e6e0d5;background:{bg};'
                        f'color:{col};font-weight:{w};line-height:1.7;">{txt}</td>')
            tbl.append("<tr>" + "".join(cell(c) for c in r) + "</tr>")
        tbl.append("</table>")
        out.append("".join(tbl))
        continue
    else:
        out.append(P.format(inline(ln)))
    i += 1

joined = "".join(out)
if a.divider_before:
    sig = P.format(inline(a.divider_before))
    joined = joined.replace(sig, DIV + sig)

note = (f'<p style="margin:30px 0 0;font-size:12px;color:#999999;line-height:1.7;">'
        f'{html.escape(NOTE_TEXT)}</p>') if NOTE_TEXT.strip() else ""

doc = (f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>{html.escape(a.title)}</title></head>'
       '<body style="margin:0;background:#ffffff;"><div style="max-width:677px;margin:0 auto;padding:24px 16px;">'
       + joined + note + '</div></body></html>')
pathlib.Path(a.out).write_text(doc, encoding="utf-8")
print("章节数", n, "｜重点句", joined.count(f"background:{HILITE};color:{INK}"), "｜字符", len(doc))
