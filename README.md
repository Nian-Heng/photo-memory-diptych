# Photo Memory Diptych 照片记忆面板

把一张照片变成「忠实原片 + 定制抽象面板 + 诗意英文标题」的竖版编辑作品。
**铁律：原照片一像素都不动** —— 这是它区别于多数"AI 重画"类工具的地方。

## 它是什么

输入一张照片，输出一张竖版图：上方是原照片（只等比缩放、绝不重画），
下方是一块干净的中性象牙色抽象面板，面板上是**AI 看着这张照片量身定制的抽象图案**，
配一个 AI 现场起的 2–5 词诗意英文标题。

它不是滤镜，不是风格迁移，不是照片海报化。它是把一张照片做成"记忆"——
**发什么就画什么**：发彩窗就画拱窗、发老建筑就画尖顶窗棂、发云就画云的形态、发动物就画动物。

## 特色

- **动态定制抽象**：不是固定模板。AI 先读照片，提取主体、主色调、形态，再据此生成贴合照片的抽象图案。
- **AI 诗意标题**：标题由 AI 看着照片现场起，每张照片独一无二。
- **标题自动避让**：英文标题自动检测空白位置摆放，绝不压住抽象图案。
- **单色无接缝**：面板底色取自动生成图的实际背景色，两层合一，干净统一。
- **原片忠实**：上方原照片一个像素都不动，只等比缩放。

## 快速开始

```bash
# 依赖 Pillow + 需要 SiliconFlow API key（环境变量 SILICONFLOW_KEY）
pip3 install Pillow
export SILICONFLOW_KEY="sk-你的key"

# 自动模式：按照片内容生成抽象 + AI 起标题
python3 scripts/photo_memory_diptych.py input.jpg output.png

# 自定义标题
python3 scripts/photo_memory_diptych.py input.jpg output.png "My Title"
```

## 内容结构

```text
photo-memory-diptych/
├── SKILL.md          # Agent 工作流与铁律
├── README.md
├── LICENSE           # MIT
└── scripts/
    └── photo_memory_diptych.py   # AI 定制抽象合成（原片不动）
```

## 两点核心原则

1. 上传照片永远是唯一内容来源，照片区域不允许被重画、扩展或改写。
2. 抽象面板里每个重要元素都必须能追溯到原照片真实存在的空间、色彩或结构事实。

## 许可

MIT License —— 由沈珩 & 念念（Nian-Heng）共同创作，开源共享。
