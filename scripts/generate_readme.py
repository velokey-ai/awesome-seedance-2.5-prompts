#!/usr/bin/env python3
"""排版机器人：读 data/prompts.yaml，生成 README.md（英文）+ README_zh.md（中文）。
本地跑：python3 scripts/generate_readme.py
线上：GitHub Actions 在数据变化或每天定时自动跑。"""
import os
import datetime
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "prompts.yaml")

REPO = "velokey-ai/awesome-seedance-2.5-prompts"
SITE = "https://velokey.ai?sourceChannel=github-awesome-seedance"
BANNER = "images/banner.png"  # 顶部横幅，images/ 下存在才会显示

# ---------------- 分类注册表 ----------------
# 素材表里 category 填左边的 key；新增分类在这里加一行即可
CATEGORIES = {
    "cinematic":   {"zh": "电影运镜",     "en": "Cinematic",            "emoji": "🎞️"},
    "character":   {"zh": "角色动作",     "en": "Character & Action",   "emoji": "🕺"},
    "product":     {"zh": "产品广告",     "en": "Product & Ads",        "emoji": "🛍️"},
    "anime":       {"zh": "动漫二次元",   "en": "Anime & Stylized",     "emoji": "🌸"},
    "vfx":         {"zh": "特效转场",     "en": "VFX & Transitions",    "emoji": "✨"},
    "scene":       {"zh": "场景氛围",     "en": "Scenery & Mood",       "emoji": "🌆"},
    "other":       {"zh": "其他",         "en": "Others",               "emoji": "📦"},
}

TEXT = {
    "en": {
        "title": "🎬 Awesome Seedance 2.5 Prompts",
        "intro": (
            "> A curated collection of creative **video** prompts for ByteDance's **Seedance 2.5** "
            "video model, collected from the community with attribution.\n>\n"
            "> ⚡ Try every prompt through one OpenAI-compatible API — "
            f"**[Velokey]({SITE})** gives you Seedance, Kling, Veo, Sora and more "
            "with a single key, pay-as-you-go."
        ),
        "copyright": (
            "> ⚠️ **Copyright**: All prompts and preview frames are collected from public community "
            "posts for educational purposes, with author attribution and source links. "
            "If any content infringes your rights, please open an issue and we will remove it promptly."
        ),
        "stats": "📊 Statistics", "total": "📝 Total Prompts", "featured_c": "⭐ Featured",
        "cats": "🏷️ Categories", "updated": "🔄 Last Updated",
        "toc": "🗂️ Browse by Category",
        "all_sec": "📋 All Prompts",
        "prompt": "📝 Prompt", "note": "💡 Note",
        "needs_input": "**Input:** upload a reference image",
        "watch": "▶️ Watch the video on X",
        "credit": "👤 Credit", "via": "collected via",
        "contribute": "🤝 How to Contribute",
        "contribute_body": (
            "Found a great prompt on X / Reddit / RedNote? "
            f"[**Submit it via Issue form**](https://github.com/{REPO}/issues/new?template=submit-prompt.yml) "
            "— once approved, it appears in the README automatically."
        ),
        "try_line": f"▶️ **Run this prompt via API** → [Velokey]({SITE}) (model id: `{{model}}`)",
        "license": "📄 License",
        "license_body": "Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Prompt credits belong to their original authors.",
        "lang_switch": "**English** · [简体中文](README_zh.md)",
        "footer": f"One API for leading text, image & video models · [velokey.ai]({SITE})",
    },
    "zh": {
        "title": "🎬 Seedance 2.5 神级视频提示词合集",
        "intro": (
            "> 精选社区疯传的 **Seedance 2.5** 创意**视频**提示词，全部标注原作者与出处。\n>\n"
            f"> ⚡ 想直接跑这些提示词？**[Velokey]({SITE})** 一个 API 调用 Seedance、"
            "Kling、Veo、Sora 等主流视频模型，一个 Key，按量付费。"
        ),
        "copyright": (
            "> ⚠️ **版权说明**：所有提示词与预览帧均收集自公开社区帖子，仅作学习交流，"
            "均已标注作者与来源。如有侵权请提 Issue，我们会第一时间删除。"
        ),
        "stats": "📊 数据统计", "total": "📝 提示词总数", "featured_c": "⭐ 精选",
        "cats": "🏷️ 分类数", "updated": "🔄 最近更新",
        "toc": "🗂️ 按分类浏览",
        "all_sec": "📋 全部提示词",
        "prompt": "📝 提示词", "note": "💡 使用说明",
        "needs_input": "**输入：** 需上传一张参考图",
        "watch": "▶️ 在 X 上观看视频",
        "credit": "👤 出处", "via": "转自",
        "contribute": "🤝 投稿",
        "contribute_body": (
            "在 X / Reddit / 小红书看到好提示词？"
            f"[**点这里用表单投稿**](https://github.com/{REPO}/issues/new?template=submit-prompt.yml)"
            "，审核通过后自动收录进 README。"
        ),
        "try_line": f"▶️ **用 API 跑这条提示词** → [Velokey]({SITE})（模型 id：`{{model}}`）",
        "license": "📄 协议",
        "license_body": "本仓库采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 协议，提示词版权归原作者所有。",
        "lang_switch": "[English](README.md) · **简体中文**",
        "footer": f"一个 API 接入主流文本 / 图片 / 视频模型 · [velokey.ai]({SITE})",
    },
}


def anchor(text):
    keep = []
    for ch in text.lower():
        if ch.isalnum() or ch == " " or ch == "-" or "一" <= ch <= "鿿":
            keep.append(ch)
    return "".join(keep).strip().replace(" ", "-")


def cat_of(p):
    key = p.get("category", "other")
    return key if key in CATEGORIES else "other"


def cat_label(key, lang):
    c = CATEGORIES[key]
    return f"{c['emoji']} {c[lang]}"


def entry_md(p, t, lang):
    title = p["title"] if lang == "zh" else p.get("title_en", p["title"])
    ckey = cat_of(p)
    cname = CATEGORIES[ckey][lang]
    lines = [f"### No.{p['id']} {title}", ""]
    badges = [
        f"![Category](https://img.shields.io/badge/{'分类' if lang=='zh' else 'category'}-{cname.replace(' ', '_').replace('-', '--')}-8A2BE2)",
        f"![Model](https://img.shields.io/badge/model-{p.get('model','seedance-2.5').replace('-','--')}-blue)",
    ]
    if p.get("featured"):
        badges.append("![Featured](https://img.shields.io/badge/%E2%AD%90-Featured-gold)")
    if p.get("needs_input"):
        badges.append("![Needs input](https://img.shields.io/badge/needs-reference_image-orange)")
    lines += [" ".join(badges), ""]
    # 视频仓：封面帧可点击跳原推文观看视频（方案 B）；图片懒加载
    imgs = p.get("images", [])
    src = p.get("source", "#")
    if imgs:
        cells = " ".join(
            f'<a href="{src}"><img src="images/{f}" width="420" loading="lazy" alt="{title}"></a>'
            for f in imgs if not f.lower().endswith((".mp4", ".mov", ".webm"))
        )
        lines += ["<div align=\"center\">", "", cells, "",
                  f'<a href="{src}"><b>{t["watch"]}</b></a>', "", "</div>", ""]
    # prompt 默认折叠，点击展开（避免一条占满整屏）
    lines += ["<details>", f"<summary>{t['prompt']}</summary>", "", "```", p["prompt"].strip(), "```", "", "</details>", ""]
    if p.get("needs_input"):
        lines += [t["needs_input"], ""]
    if p.get("note"):
        lines += [f"> {t['note']}: {p['note']}", ""]
    credit = f"**{t['credit']}:** [{p['author']}]({p['author_link']}) · [source]({p['source']})"
    if p.get("via"):
        credit += f" · {t['via']} {p['via']}"
    lines += [credit, "", t["try_line"].replace("{model}", p.get("model", "seedance-2.5")), ""]
    lines += ["---", ""]
    return "\n".join(lines)


def build(lang):
    t = TEXT[lang]
    with open(DATA, encoding="utf-8") as f:
        prompts = yaml.safe_load(f) or []
    prompts.sort(key=lambda p: (not p.get("featured", False), p["id"]))
    featured = [p for p in prompts if p.get("featured")]
    used_cats = [k for k in CATEGORIES if any(cat_of(p) == k for p in prompts)]
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    md = []
    if os.path.exists(os.path.join(ROOT, BANNER)):
        md.append(f'<a href="{SITE}"><img src="{BANNER}" width="100%" alt="Awesome Seedance 2.5 Prompts"></a>\n')
    md.append(f"# {t['title']}\n")
    md.append(t["lang_switch"] + "\n")
    md.append("[![Awesome](https://awesome.re/badge.svg)](https://github.com/sindresorhus/awesome) "
              f"[![PRs Welcome](https://img.shields.io/badge/submissions-welcome-brightgreen.svg)](https://github.com/{REPO}/issues/new?template=submit-prompt.yml) "
              "[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)\n")
    md.append(t["intro"] + "\n")
    md.append(t["copyright"] + "\n")

    md.append(f"## {t['stats']}\n")
    md.append(f"| {t['total']} | {t['featured_c']} | {t['cats']} | {t['updated']} |")
    md.append("|---|---|---|---|")
    md.append(f"| **{len(prompts)}** | **{len(featured)}** | **{len(used_cats)}** | {now} |\n")

    md.append(f"## {t['toc']}\n")
    for ckey in used_cats:
        group = [p for p in prompts if cat_of(p) == ckey]
        md.append(f"<details open><summary><b>{cat_label(ckey, lang)}</b> ({len(group)})</summary>\n")
        for p in group:
            title = p["title"] if lang == "zh" else p.get("title_en", p["title"])
            star = "⭐ " if p.get("featured") else ""
            md.append(f"- [{star}No.{p['id']} {title}](#no{p['id']}-{anchor(title)})")
        md.append("\n</details>\n")

    md.append(f"## {t['all_sec']}\n")
    for p in prompts:
        md.append(entry_md(p, t, lang))

    md.append(f"## {t['contribute']}\n")
    md.append(t["contribute_body"] + "\n")
    md.append(f"## {t['license']}\n")
    md.append(t["license_body"] + "\n")
    md.append(f"[![Star History Chart](https://api.star-history.com/svg?repos={REPO}&type=Date)](https://star-history.com/#{REPO}&Date)\n")
    md.append("<div align=\"center\">\n")
    md.append(f"<sub>🤖 Auto-generated from <code>data/prompts.yaml</code> · {now}</sub>\n")
    md.append(f"<br><sub>{t['footer']}</sub>\n")
    md.append("</div>")
    return "\n".join(md)


if __name__ == "__main__":
    for lang, fname in (("en", "README.md"), ("zh", "README_zh.md")):
        out = build(lang)
        path = os.path.join(ROOT, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"✅ {fname} generated")
