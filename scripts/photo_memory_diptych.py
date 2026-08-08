#!/usr/bin/env python3
"""photo-memory-diptych 整合版脚本(AI 按照片内容生成抽象面板)

把一张照片做成「忠实原片 + 抽象记忆面板 + 诗意英文标题」的竖版编辑作品。
抽象面板不再是固定模板，而是 AI 先读照片，按要求身定制的抽象图案生成，
再拼到底部象牙面板。标题也由 AI 看着照片现场起。

用法:
    python3 photo_memory_diptych.py <输入图.jpg> <输出图.png> ["可选标题"]
    (不传标题 → 自动用 AI 读图起 2-5 词诗意英文标题)

依赖: Pillow (PIL)。
AI 能力: SiliconFlow (key: environment SILICONFLOW_KEY 或下方默认)。
  - 文生图 Qwen/Qwen-Image      生成定制抽象图案
  - 多模态 Qwen3-VL-32B         读照片得到主题/主色/抽象描述 + 起标题

流程:
  1. AI 读原照片 → 提取主体、主色调、该画什么抽象母题(贴合照片内容, 非固定模板)
  2. 按该描述让 AI 生成定制抽象直出图(象牙底)
  3. 原照片等比贴画布顶部(一像素不动)
  4. 面板底色 = 定制造图真实背景色(取四角), 两层背景合一, 单色无接缝
  5. AI 读原照片起 2-5 词诗意英文标题, 衬线体放面板中下部
"""
import os
import sys
import json
import base64
import urllib.request
import urllib.error
from PIL import Image, ImageDraw, ImageFont

SILICONFLOW_BASE = "https://api.siliconflow.cn/v1"
DEFAULT_KEY = "sk-aamycyltxjhzoohyzkjhqjdeurgfiyvvprgpmdmbbpxwlsuz"
AI_MODEL = "Qwen/Qwen-Image"          # 文生图
VL_MODEL = "Qwen/Qwen3-VL-32B-Instruct"  # 多模态读图
AI_SIZE = "832x1248"                  # 竖版抽象图

SERIF_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
]

FALLBACK_ABSTRACT = (
    "纯色背景上,一个极简蓝金抽象图案:下方五根并排竖条(三根藏青一根金黄再一根藏青),"
    "上方一个三角拱顶左半金黄右半藏青。图案居中,留大片空白,"
    "无边框无渐变无文字无阴影,扁平极简,拱窗几何母题。"
)


def get_key():
    return os.environ.get("SILICONFLOW_KEY", DEFAULT_KEY)


def _chat(messages, max_tokens):
    """通用 SiliconFlow chat 调用,返回首个文本回复。"""
    payload = {"model": VL_MODEL, "messages": messages, "max_tokens": max_tokens}
    req = urllib.request.Request(
        SILICONFLOW_BASE + "/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + get_key(), "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read().decode())
    return d["choices"][0]["message"]["content"].strip()


def _with_image_b64(path, text, max_tokens):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": text},
            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}},
        ],
    }]
    return _chat(messages, max_tokens)


def ai_title_from_photo(photo_path):
    """AI 看照片起 2-5 词诗意英文标题。"""
    title = _with_image_b64(
        photo_path,
        "看这张照片, 用英文起一个2到5个词的诗意短片名/标题, 贴合照片内容、光线、情绪。"
        "只输出标题本身, 不要解释, 不要引号。",
        40,
    )
    title = title.strip("\"'…")
    print("AI 看图起标题:", repr(title))
    return title or "Light Divides the Arch"


def ai_abstract_description(photo_path):
    """AI 读照片, 返回贴合该主体的抽象图案描述(SUBJECT/COLORS/MOTIF)。"""
    desc = _with_image_b64(
        photo_path,
        "分析这张照片:1)主体是什么(30字内) 2)主色调(给2-3个颜色) "
        "3)用一句话描述该画一个什么样的极简抽象图案来提炼这张照片(几何形态, 贴合主体)。"
        "用英文输出这三项, 每项前加标签: SUBJECT: / COLORS: / MOTIF: ",
        130,
    )
    print("AI 抽象描述:", desc.replace("\n", " "))
    return desc


def build_abstract_prompt(desc):
    """把 AI 抽象描述包装成文生图提示词, 硬性保证单色纯背景。"""
    return (
        f"极简扁平抽象几何图案: {desc}。"
        "背景必须是干净的单一象牙白纯色, 背景上绝对不允许出现任何圆形、色块、圆圈、"
        "边框、衬底、描边或额外形状作为'容器'——图案直接画在这个纯色背景上。"
        "图案居中, 无文字无渐变无阴影, 配色从照片中提炼, 背景纯色无任何装饰。"
    )


def ai_generate_abstract(out_path, prompt=None, size=AI_SIZE):
    """调 SiliconFlow 文生图, 生成抽象直出图。prompt 不传则用默认蓝金拱窗。"""
    final_prompt = prompt or FALLBACK_ABSTRACT
    payload = {
        "model": AI_MODEL,
        "prompt": final_prompt,
        "image_size": size,
        "batch_size": 1,
    }
    req = urllib.request.Request(
        SILICONFLOW_BASE + "/images/generations",
        data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + get_key(), "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.loads(r.read().decode())
    url = d["images"][0]["url"] if isinstance(d["images"][0], dict) else d["images"][0]
    if not url:
        raise RuntimeError("AI 生成未返回图片 URL")
    with urllib.request.urlopen(url, timeout=60) as fr:
        with open(out_path, "wb") as f:
            f.write(fr.read())
    print("AI 抽象图已生成 ->", out_path)
    return out_path


def dominant_bg_color(img):
    """从图片四角取样,返回背景主色(四角平均值)。"""
    w, h = img.size
    px = img.load()
    corners = [px[3, 3], px[w - 4, 3], px[3, h - 4], px[w - 4, h - 4]]
    r = sum(c[0] for c in corners) // 4
    g = sum(c[1] for c in corners) // 4
    b = sum(c[2] for c in corners) // 4
    return (r, g, b)


def find_serif():
    for fp in SERIF_CANDIDATES:
        if os.path.exists(fp):
            return fp
    for root, _, files in os.walk("/usr/share/fonts"):
        for f in files:
            if f.lower().endswith((".ttf", ".ttc")):
                return os.path.join(root, f)
    raise SystemExit("no serif font found")


def compose(photo_path, ai_path, out_path, title):
    """拼版:照片在上 + 面板底色=AI图背景色 + AI图主体居中 + 标题。"""
    photo = Image.open(photo_path).convert("RGB")
    ai = Image.open(ai_path).convert("RGB")
    pw, ph = photo.size
    aw, ah = ai.size

    # 面板底色 = AI 图真实背景色(两层背景合一)
    bg = dominant_bg_color(ai)

    panel_h = int(ph * 0.42)
    canvas_h = ph + panel_h
    canvas = Image.new("RGB", (pw, canvas_h), bg)
    canvas.paste(photo.resize((pw, ph)), (0, 0))

    d = ImageDraw.Draw(canvas)
    panel_top = ph
    d.rectangle([0, panel_top, pw, canvas_h], fill=bg)

    # AI 抽象图主体等比缩放,面板宽约 62%,居中
    ai_tw = int(pw * 0.62)
    ai_th = int(ah * ai_tw / aw)
    if ai_th > panel_h * 0.9:
        ai_th = int(panel_h * 0.9)
        ai_tw = int(aw * ai_th / ah)
    ai_scaled = ai.resize((ai_tw, ai_th))
    x0 = (pw - ai_tw) // 2
    y0 = panel_top + (panel_h - ai_th) // 2
    canvas.paste(ai_scaled, (x0, y0))

    # ===== 动态标题避让: 英文绝不压抽象图 =====
    title_font = 34
    f = ImageFont.truetype(find_serif(), title_font)
    title_w = d.textlength(title, font=f) if hasattr(d, "textlength") else len(title) * title_font

    def is_blank(x, y):
        """判断画布某点是否接近背景色(空白)。"""
        if x < 0 or y < 0 or x >= pw or y >= canvas_h:
            return False
        c = canvas.getpixel((x, y))
        return all(abs(c[i] - bg[i]) < 18 for i in range(3))

    def candidate_is_blank(tx, ty):
        """标题所在横条区域是否全部空白(不压图)。"""
        for xx in range(int(tx), min(int(tx + title_w), pw - 1)):
            for yy in range(int(ty), int(ty + title_font)):
                if not is_blank(xx, yy):
                    return False
        return True

    # 候选位置: 优先级从上到下
    candidates = []
    # 1) 抽象图正下方的留白区(原逻辑)
    under = y0 + ai_th + int(title_font * 0.9)
    if under + title_font <= panel_top + panel_h and candidate_is_blank(pw * 0.08, under):
        candidates.append((pw * 0.08, under))
    if under + title_font <= panel_top + panel_h and candidate_is_blank(pw * 0.32, under):
        candidates.append((pw * 0.32, under))
    # 2) 图右侧空白区(若图偏左)
    right_x = x0 + ai_tw + int(pw * 0.02)
    right_y = y0
    if right_x + title_w <= pw and candidate_is_blank(right_x, right_y):
        candidates.append((right_x, right_y))
    # 3) 图左侧空白区(若图偏右)
    left_x = x0 - title_w - int(pw * 0.02)
    if left_x >= 0 and candidate_is_blank(left_x, y0):
        candidates.append((left_x, y0))
    # 4) 面板底角兜底
    bottom_y = panel_top + panel_h - title_font - int(title_font * 0.5)
    if candidate_is_blank(pw * 0.08, bottom_y):
        candidates.append((pw * 0.08, bottom_y))
    if candidate_is_blank(pw - title_w - pw * 0.08, bottom_y):
        candidates.append((pw - title_w - pw * 0.08, bottom_y))

    if candidates:
        tx, ty = candidates[0]
    else:
        # 兜底: 图上方抬, 标题放最低部
        tx, ty = pw * 0.08, panel_top + panel_h - title_font
    d.text((tx, ty), title, font=f, fill=(25, 25, 25))

    canvas.save(out_path)
    print("saved", out_path, canvas.size)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    src, out = sys.argv[1], sys.argv[2]

    # 1. AI 读照片定定制抽象描述 + 起标题
    desc = ai_abstract_description(src)
    prompt = build_abstract_prompt(desc)
    if len(sys.argv) >= 4:
        title = " ".join(sys.argv[3:])
    else:
        title = ai_title_from_photo(src)

    # 2. 生成定制抽象图 + 拼版
    tmp_ai = out + ".tmp_ai.png"
    try:
        ai_generate_abstract(tmp_ai, prompt=prompt)
        compose(src, tmp_ai, out, title)
    finally:
        if os.path.exists(tmp_ai):
            os.remove(tmp_ai)


if __name__ == "__main__":
    main()
