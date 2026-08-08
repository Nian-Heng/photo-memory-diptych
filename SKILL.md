---
name: photo-memory-diptych
description: 把一张照片做成「忠实原片 + 抽象记忆面板 + 诗意英文标题」的竖版编辑作品。铁律：原照片一像素不动。Use when asked to turn a photo into an abstract memory diptych, photo-plus-abstraction panel, minimalist archival poster, or visual memory card while keeping the source photo completely intact.
---

# Photo Memory Diptych 照片记忆面板

把一张照片做成「忠实原片 + 抽象记忆面板 + 诗意英文标题」的竖版编辑作品。

## 铁律（最重要）

上传照片是唯一内容来源。照片区域只允许等比缩放，**绝不允许重画、扩展、改写、修饰、加滤镜**。
抽象面板里的每个色块/线条/标题，都必须能回溯到原照片真实存在的空间、色彩或结构事实。

为什么：AI 直出/图像编辑模型实测会把照片"艺术化重画"，照片一变原味就没了。
所以本 skill 用**程序化合成**保证 100% 保真。

## 工作流

1. 读原照片，识别 3–6 个决定性空间事实：主体关系、轴线、节奏、明暗、色彩角色、留白。
2. 程序把照片等比贴画布顶部/主要区域，一像素不动（用 Pillow paste + resize，不重绘）。
3. 下方铺纯象牙色面板 `#F3F0E8`（无渐变、无纹理、无阴影、无装饰）。
4. 从照片提 1 主色 + 1 强调色（实测彩窗照片 = 克莱因蓝 + 琥珀金）。
5. 面板上画极简母题：尖拱 + 竖条节奏模拟拱窗（宁可少、宁可留白）。
6. 面板中下部放 2–5 词衬线英文标题，左下安全距 6–9%。

## 执行脚本

`scripts/photo_memory_diptych.py` —— 保真程序化合成，用 Pillow 实现全流程。

```bash
python3 scripts/photo_memory_diptych.py input.jpg output.png "Light Divides the Arch"
```

- 依赖：Pillow（`pip3 install Pillow`）
- 字体：优先 DejaVuSerif / LiberationSerif / FreeSerif，找不到扫 /usr/share/fonts
- 竖版高耸主体默认纵向布局（照片区 62% + 面板 38%）

## 输出前验证（必做）

交给用户前，先用视觉检查确认：
1. 原照片未重画（一像素没动）
2. 面板干净无渐变无纹理
3. 标题清晰、居中/左下、可读

## 参考：可用的生图通道（可选增强）

如果想走 AI 增强面板（可选，非保真方案），实测 SiliconFlow：
- base_url `https://api.siliconflow.cn/v1`，文生图 POST `/v1/images/generations`
- model `Qwen/Qwen-Image` 可直出；`Qwen/Qwen-Image-Edit` 需带 `image` 字段但会把照片重画，慎用
- 纯 AI 直出保不住原照片，只作风格参考，不用于交付保真作品
