#!/usr/bin/env python3
"""photo-memory-diptych 保真合成脚本 (原创程序方案, 非AI重画)

原照片等比贴画布顶部（一像素不动）+ 下方象牙色抽象面板 + 蓝金拱窗母题 + 衬线英文标题。
用于规避 Qwen-Image-Edit 会重画原照片的问题，满足 skill 铁律「照片不得重画」。

用法:
    python3 photo_abstract_diptych.py <输入图.jpg> <输出图.png> ["Light Divides the Arch"]

依赖: Pillow (PIL)。字体优先 DejaVuSerif，找不到就扫 /usr/share/fonts。
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

IVORY = (243, 240, 232)  # #F3F0E8
SERIF_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
]


def find_serif():
    for fp in SERIF_CANDIDATES:
        if os.path.exists(fp):
            return fp
    for root, _, files in os.walk("/usr/share/fonts"):
        for f in files:
            if f.lower().endswith((".ttf", ".ttc")):
                return os.path.join(root, f)
    raise SystemExit("no serif font found")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    src, out = sys.argv[1], sys.argv[2]
    title = " ".join(sys.argv[3:]) or "Light Divides the Arch"

    photo = Image.open(src).convert("RGB")
    w, h = photo.size

    # 纵向建筑/竖版照片:照片区约 62%,面板约 38%(按实际照片方向微调比例)
    photo_h = h
    panel_h = int(photo_h * 0.42)
    canvas = Image.new("RGB", (w, photo_h + panel_h), IVORY)
    canvas.paste(photo.resize((w, photo_h)), (0, 0))  # 等比缩放,不重画

    d = ImageDraw.Draw(canvas)
    panel_top = photo_h
    d.rectangle([0, panel_top, w, photo_h + panel_h], fill=IVORY)

    # 从照片提色的主色(可按照片实际颜色改) — 彩窗蓝 + 金
    blue, gold = (30, 60, 120), (198, 155, 60)

    # 抽象母题:极简尖拱 + 竖条节奏,模拟拱窗;放在面板中下部,居中
    mw = int(w * 0.38)
    mx0 = (w - mw) // 2
    my0 = panel_top + int(panel_h * 0.28)
    mh = int(panel_h * 0.34)
    arch_h = int(mh * 0.4)

    # 中央双色尖拱(不对称更接近"观察所得"而非对称图标)
    d.polygon([(mx0 + mw * 0.30, my0 + arch_h), (mx0 + mw * 0.50, my0), (mx0 + mw * 0.70, my0 + arch_h)], fill=gold)
    d.polygon([(mx0 + mw * 0.45, my0 + arch_h), (mx0 + mw * 0.50, my0), (mx0 + mw * 0.75, my0 + arch_h)], fill=blue)

    # 竖条节奏(蓝蓝金蓝),与拱窗竖格对应
    for (bx0, bx1), c in [
        ((0.10, 0.22), blue), ((0.30, 0.42), blue),
        ((0.50, 0.62), gold), ((0.70, 0.90), blue),
    ]:
        d.rectangle([mx0 + mw * bx0, my0 + arch_h + 6, mx0 + mw * bx1, my0 + mh], fill=c)

    # 衬线标题,左下安全距(约 6-9%)
    f = ImageFont.truetype(find_serif(), 44)
    d.text((int(w * 0.08), photo_h + panel_h - int(panel_h * 0.28)), title, font=f, fill=(25, 25, 25))

    canvas.save(out)
    print("saved", out, canvas.size)


if __name__ == "__main__":
    main()
