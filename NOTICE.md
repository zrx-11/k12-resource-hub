# NOTICE · 第三方来源与许可

本项目（K12 资源枢纽）是个人非商业站点。以下列出站内使用的第三方内容与许可；如与上游最新声明不一致，以上游为准。

## 1. chinese-poetry

- 项目：https://github.com/chinese-poetry/chinese-poetry
- 许可：MIT
- 用途：抽取蒙学、诗经、论语、唐诗、宋诗、宋词、元曲常用篇目，生成 `data/poetry.json`
- 改动：简繁转换为简体（OpenCC t2s）；按名篇清单筛选；未改动诗文正文

## 2. hanzi-writer

- 项目：https://github.com/chanind/hanzi-writer
- 许可：MIT（代码）
- 用途：汉字笔顺动画、描红练习
- 文件：`assets/hanzi-writer.min.js`

## 3. Make Me a Hanzi / hanzi-writer-data

- 项目：https://github.com/skishore/makemeahanzi
- 数据包：https://www.npmjs.com/package/hanzi-writer-data
- 许可：字形数据按 Arphic Public License；字典数据 LGPL
- 用途：9000+ 汉字的笔顺、字形数据
- 文件：`data/hanzi/*.json`、`data/hanzi/ARPHICPL.TXT`、`data/hanzi/APL/`
- 改动：无；按原文件复制

## 4. pinyin-pro

- 项目：https://github.com/zh-lx/pinyin-pro
- 许可：MIT
- 用途：汉字转拼音、多音字、声母/韵母
- 文件：`assets/pinyin-pro.js`

## 5. cn-math-taxonomy

- 项目：https://github.com/xiaoyang111222/cn-math-taxonomy
- 生产站点：https://math.pansgo.com/
- 许可：CC BY-NC 4.0（https://creativecommons.org/licenses/by-nc/4.0/deed.zh-hans）
- 用途：中小学·高中知识图谱、先修诊断、题库的非商业静态镜像
- 位置：`/cn-math-taxonomy/`
- 改动：调整部署路径；隐藏上游推广横幅（儿童智商测试、学习好物卡）；增加 `NOTICE.md`；未修改知识点、先修关系、题目与诊断逻辑
- 限制：不得用于付费课程、付费 App、机构收费服务、售卖题库等商业用途

## 6. 仅链接、不托管的内容

以下内容仅在资源目录中提供链接，不在本仓库/站点托管：

- 国家中小学智慧教育平台、人教社教材电子版、省级教育平台
- ChinaTextbook、tchMaterial-parser、ChinaTextbook-tools
- 莲山课件、第一课件网、绿色圃、学科网、21世纪教育网、菁优网、组卷网、中国教育出版网
- CK-12、OpenStax、Illustrative Mathematics、Open Up Resources、PhET、GeoGebra、Khan Academy、OER Commons、Code.org
- 学之思、SmartKBS、wrong-notebook、题有据、MidAnswer 等需要后端/数据库/桌面运行的项目

这些资源的版权、许可、免费政策由原站/原仓库决定；本站不做授权，也不保证链接长期有效。

## 7. 侵权处理

如果你是权利人，认为本站内容侵犯了你的权益，请在
<https://github.com/zrx-11/k12-resource-hub/issues>
说明具体页面与权利依据，我会尽快处理或移除。
