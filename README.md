# 个人知识库

把零散的金句、截图、文档、链接，规范化沉淀为可检索的私人书库。
由 Claude（knowledge-base-builder skill）自动维护。

## 结构
- `entries/` — 每条知识一个 Markdown 文件（带 YAML frontmatter）
- `assets/` — 图片/截图原件
- `build.py` — 扫描 entries → manifest.json → 注入 template.html → index.html
- `template.html` — 总览页模板（设计一次成型，勿手改样式）
- `index.html` — 自动生成的总览页（带搜索/分类/跳转，勿手改）
- `manifest.json` — 自动生成的索引

## 用法
新增知识后，在仓库根目录运行：`python3 build.py`，然后提交即可。
