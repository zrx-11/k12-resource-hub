# K12 资源枢纽

一个个人非商业的中小学资源导航与轻量工具站，部署在 GitHub Pages：
<https://zrx-11.github.io/k12-resource-hub/>

## 站点内容

| 路径 | 内容 |
|---|---|
| `/` | 53 项资源索引：官方平台、教材获取、课件试卷、开放教材、开源项目 |
| `/poetry/` | 古诗文阅读库：蒙学、诗经、论语、唐诗、宋诗、宋词、元曲，约 477 篇 |
| `/hanzi/` | 汉字笔顺：9000+ 汉字笔顺动画、描红、拼音与笔画数 |
| `/pinyin/` | 拼音标注：声调符号/数字/无声调、多音字、逐字对照 |
| `/cn-math-taxonomy/` | 中小学·高中知识图谱的非商业静态镜像（CC BY-NC 4.0） |
| `/downloads/` | 下载指南：哪些已下载、哪些可下载、哪些不适合 Pages 托管 |
| `/about/` | 来源、许可、免责声明 |

## 构建

需要：`git`、`node`（18+）、`python3`、`opencc-python-reimplemented`。

```bash
pip install opencc-python-reimplemented
python3 scripts/prepare_assets.py
python3 -m http.server 8000 -d dist
```

首次构建会从公开仓库/包管理器拉取：

- `chinese-poetry`（MIT）
- `hanzi-writer-data`（Arphic Public License）
- `hanzi-writer`（MIT）
- `pinyin-pro`（MIT）
- `cn-math-taxonomy`（CC BY-NC 4.0）

产物 `dist/` 约 80–110MB，GitHub Pages 可直接托管。大体积教材 PDF、商业题库、需要后端/数据库的项目不在本站托管。

## 部署

`.github/workflows/pages.yml` 在 push 到 `main` 时自动构建并部署到 GitHub Pages。`configure-pages` 带 `enablement: true`，首次运行会尝试为仓库启用 Pages。

## 许可

本站原创代码采用 MIT；资源目录文本采用 CC BY 4.0。第三方数据/库按各自许可证使用，详见 `NOTICE.md` 与站点 `/about/` 页。教材 PDF 版权归原出版社，不在本站托管。
