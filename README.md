# Photo Memory Diptych 照片记忆面板

把一张照片变成「忠实原片 + 抽象记忆面板 + 诗意英文标题」的竖版编辑作品。
**铁律：原照片一像素都不动** —— 这是它区别于多数"AI 重画"类工具的地方。

## 它是什么

输入一张照片，输出一张竖版图：上方是原照片（只等比缩放、绝不重画），
下方是一块干净的中性象牙色抽象面板，面板上是**从照片本身提炼颜色与空间节奏**画的极简母题，
配一个优雅衬线字体的 2–5 词英文标题。

它不是滤镜，不是风格迁移，不是照片海报化。它是把一张照片做成"记忆"——
抽象层每个色块、每根线条都能回溯到原照片真实存在的空间、色彩或结构事实。

## 为什么用程序合成，而不是纯 AI 直出

实测（SiliconFlow Qwen/Qwen-Image-Edit）：**多数图像编辑/直出模型会把上传照片"艺术化重画"成几何图形**，
拒绝老老实实保留原照。这违反"照片不得重画"的铁律 —— 照片一变，原味就没了。

因此本方案采用**程序化合成**，保证 100% 保真：
- 原照片等比贴画布顶部（一个像素都不动）
- 下方铺纯象牙色面板 `#F3F0E8`，无渐变、无纹理、无阴影
- 从照片提取主色，画极简记忆母题
- 衬线字体英文标题放面板中下部

## 快速开始

```bash
# 依赖 Pillow
pip3 install Pillow

# 竖版建筑/高耸主体照片（自动纵向布局）
python3 scripts/photo_memory_diptych.py input.jpg output.png "Light Divides the Arch"

# 横版/宽幅照片（自动横向布局）
python3 scripts/photo_memory_diptych.py wide.jpg out_wide.png "A Line of Light"
```

## 内容结构

```text
photo-memory-diptych/
├── SKILL.md          # Agent 工作流与铁律
├── README.md
├── LICENSE           # MIT
└── scripts/
    └── photo_memory_diptych.py   # 保真程序化合成（一像素不动）
```

## 两点核心原则

1. 上传照片永远是唯一内容来源，照片区域不允许被重画、扩展或改写。
2. 抽象面板里每个重要元素都必须能追溯到原照片真实存在的空间、色彩或结构事实。

## 许可

MIT License —— 由沈珩 & 念念（Nian-Heng）共同创作，开源共享。
