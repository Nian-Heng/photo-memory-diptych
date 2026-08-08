#!/usr/bin/env python3
"""photo-memory-diptych 合并版脚本(AI 直出抽象面板)

把一张照片做成「忠实原片 + 抽象记忆面板 + 诗意英文标题」的竖版编辑作品。
关键改进：抽象面板不再用程序画母题，而是调 SiliconFlow 文生图直接生成"蓝金拱窗
抽象图"，面板底色取该图真实背景色铺底 —— 两层背景合成一层，单色干净无接缝。

用法:
    python3 photo_memory_diptych.py <输入图.jpg> <输出图.png> ["Light Divides the Arch"]

依赖: Pillow (PIL)。
AI 抽象图生成: SiliconFlow (environment SILICONFLOW_KEY 或下方默认 key)。

流程:
  1. 原照片等比贴画布顶部(一像素不动)
  2. 调 AI 生成蓝金拱窗抽象直出图(象牙底)
  3. 面板底色 = AI 图真实背景色(取样四角), 铺成下半区, 两层背景合一
  4. AI 抽象图主体等比缩放到面板中央, 不拉伸
  5. 衬线英文标题放面板中下部
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
AI_MODEL = "Qwen/Qwen-Image"
AI_SIZE = "832x1248"  # 竖版抽象图

SERIF_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
]

AI_ABSTRACT_PROMPT = (
    "纯色背景上,一个极简的蓝金抽象图案:下方五根并排竖条(三根藏青一根金黄再一根藏青),"
    "上方一个三角拱顶左半金黄右半藏青。图案居中,留大片空白,"
    "无边框无渐变无文字无阴影,扁平极简,拱窗几何母题。"
)


def get_key():
    return os.environ.get("SILICONFLOW_KEY", DEFAULT_KEY)


def ai_generate_abstract(out_path, size=AI_SIZE):
    """调 SiliconFlow 文生图,生成蓝金拱窗抽象直出图,返回本地路径。"""
    height = int(size.split("x")[1])
    payload = {
        "model": AI_MODEL,
        "prompt": AI_ABSTRACT_PROMPT,
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

    # 衬线英文标题,左下安全距
    f = ImageFont.truetype(find_serif(), 38)
    d.text((int(pw * 0.08), panel_top + int(panel_h * 0.72)), title, font=f, fill=(25, 25, 25))

    canvas.save(out_path)
    print("saved", out_path, canvas.size)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    src, out = sys.argv[1], sys.argv[2]
    title = " ".join(sys.argv[3:]) or "Light Divides the Arch"

    tmp_ai = out + ".tmp_ai.png"
    try:
        ai_generate_abstract(tmp_ai)
        compose(src, tmp_ai, out, title)
    finally:
        if os.path.exists(tmp_ai):
            os.remove(tmp_ai)


if __name__ == "__main__":
    main()
