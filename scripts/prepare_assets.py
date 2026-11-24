# -*- coding: utf-8 -*-
"""组装 K12 资源枢纽的静态产物 dist/。

依赖：git、node、python3、opencc-python-reimplemented
构建时会从公开仓库/包管理器拉取第三方数据，仓库本身不存放大体积数据。
"""
import os
import shutil
import subprocess
import sys
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, '.cache')
DIST = os.path.join(ROOT, 'dist')
SITE = os.path.join(ROOT, 'site')

CN_MATH = 'https://github.com/xiaoyang111222/cn-math-taxonomy.git'
POETRY = 'https://github.com/chinese-poetry/chinese-poetry.git'


def run(cmd, cwd=None):
    print('+', ' '.join(cmd))
    subprocess.check_call(cmd, cwd=cwd)


def ensure_git(name, url):
    target = os.path.join(CACHE, name)
    if os.path.isdir(os.path.join(target, '.git')):
        print('cache hit:', target)
        return target
    os.makedirs(CACHE, exist_ok=True)
    run(['git', 'clone', '--depth', '1', url, target])
    return target


def ensure_npm(pkg, version):
    base = os.path.join(CACHE, 'npm', pkg)
    package = os.path.join(base, 'package')
    if os.path.isdir(package):
        print('cache hit:', package)
        return package
    os.makedirs(base, exist_ok=True)
    out = subprocess.check_output(['npm', 'pack', '%s@%s' % (pkg, version), '--silent'], cwd=base, text=True).strip()
    tgz = os.path.join(base, out.splitlines()[-1])
    run(['tar', '-xzf', tgz, '-C', base])
    return package


def copy_tree(src, dst):
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def main():
    # 0) 清理
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST, exist_ok=True)

    # 1) 站点骨架
    copy_tree(SITE, DIST)
    os.makedirs(os.path.join(DIST, 'data'), exist_ok=True)
    shutil.copy2(os.path.join(ROOT, 'data', 'resources.json'), os.path.join(DIST, 'data', 'resources.json'))
    open(os.path.join(DIST, '.nojekyll'), 'w').close()
    with open(os.path.join(DIST, 'robots.txt'), 'w', encoding='utf-8') as f:
        f.write('User-agent: *\nAllow: /\n')

    # 2) 第三方数据/库
    poetry_dir = ensure_git('chinese-poetry', POETRY)
    cn_dir = ensure_git('cn-math-taxonomy', CN_MATH)
    hanzi_data = ensure_npm('hanzi-writer-data', '2.0.1')
    hanzi_lib = ensure_npm('hanzi-writer', '3.7.3')
    pinyin_lib = ensure_npm('pinyin-pro', '3.29.5')

    # 3) 诗词库
    run([sys.executable, os.path.join(ROOT, 'scripts', 'build_poetry.py'), poetry_dir, os.path.join(DIST, 'data', 'poetry.json')])

    # 4) 汉字笔顺数据（全量 9000+ 字，按字懒加载）
    hanzi_out = os.path.join(DIST, 'data', 'hanzi')
    os.makedirs(hanzi_out, exist_ok=True)
    count = 0
    for path in glob.glob(os.path.join(hanzi_data, '*.json')):
        shutil.copy2(path, os.path.join(hanzi_out, os.path.basename(path)))
        count += 1
    for extra in ['ARPHICPL.TXT']:
        p = os.path.join(hanzi_data, extra)
        if os.path.exists(p):
            shutil.copy2(p, os.path.join(hanzi_out, extra))
    apl = os.path.join(hanzi_data, 'APL')
    if os.path.isdir(apl):
        copy_tree(apl, os.path.join(hanzi_out, 'APL'))
    print('hanzi json:', count)

    shutil.copy2(os.path.join(hanzi_lib, 'dist', 'hanzi-writer.min.js'), os.path.join(DIST, 'assets', 'hanzi-writer.min.js'))
    shutil.copy2(os.path.join(pinyin_lib, 'dist', 'index.js'), os.path.join(DIST, 'assets', 'pinyin-pro.js'))

    # 5) cn-math-taxonomy 静态镜像
    mirror = os.path.join(DIST, 'cn-math-taxonomy')
    os.makedirs(mirror, exist_ok=True)
    for name in ['index.html', 'sw.js', 'manifest.webmanifest', '.nojekyll']:
        p = os.path.join(cn_dir, name)
        if os.path.exists(p):
            shutil.copy2(p, os.path.join(mirror, name))
    for name in ['assets', 'explore', 'diagnose', 'children', 'goods', 'wrongbook', 'finals', 'english']:
        src = os.path.join(cn_dir, name)
        if os.path.isdir(src):
            copy_tree(src, os.path.join(mirror, name))
    data_out = os.path.join(mirror, 'data')
    os.makedirs(data_out, exist_ok=True)
    for name in ['topics.json', 'dependencies.json', 'cn-curriculum-standards.json', 'id-aliases.json', 'questions.json']:
        src = os.path.join(cn_dir, 'data', name)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(data_out, name))
    for name in ['questions', 'english', 'mappings']:
        src = os.path.join(cn_dir, 'data', name)
        if os.path.isdir(src):
            copy_tree(src, os.path.join(data_out, name))

    # 知识点静态页 / sitemap / robots（零依赖脚本）
    run(['node', os.path.join(cn_dir, 'scripts', 'gen-kp-pages.mjs'), '--out', mirror], cwd=cn_dir)

    # 隐藏上游的推广横幅/测评卡，保留知识图谱本体
    promo_css = '<style>.top-banner,.iq-card{display:none!important}</style>'
    for root, dirs, files in os.walk(mirror):
        for fn in files:
            if fn.endswith('.html'):
                fp = os.path.join(root, fn)
                with open(fp, encoding='utf-8') as f:
                    html = f.read()
                if '</head>' in html and promo_css not in html:
                    html = html.replace('</head>', promo_css + '</head>', 1)
                    with open(fp, 'w', encoding='utf-8') as f:
                        f.write(html)

    for name in ['LICENSE', 'README.md']:
        src = os.path.join(cn_dir, name)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(mirror, name))

    with open(os.path.join(mirror, 'NOTICE.md'), 'w', encoding='utf-8') as f:
        f.write(
            '# 镜像说明\n\n'
            '本目录是 xiaoyang111222/cn-math-taxonomy 的非商业静态镜像。\n\n'
            '- 原项目：https://github.com/xiaoyang111222/cn-math-taxonomy\n'
            '- 生产站点：https://math.pansgo.com/\n'
            '- 许可证：CC BY-NC 4.0（https://creativecommons.org/licenses/by-nc/4.0/deed.zh-hans）\n'
            '- 本站改动：调整部署路径、隐藏上游推广横幅（儿童智商测试/学习好物卡）、增加本说明；未修改知识点、先修关系、题目与诊断逻辑。\n'
            '- 用途：个人学习、教学、研究；不得用于商业用途。\n'
        )

    # 6) 体积报告
    def du(path):
        total = 0
        for root, dirs, files in os.walk(path):
            for fn in files:
                total += os.path.getsize(os.path.join(root, fn))
        return total

    print('\n=== dist size ===')
    for name in ['', 'data/poetry.json', 'data/hanzi', 'cn-math-taxonomy', 'assets']:
        p = os.path.join(DIST, name) if name else DIST
        if os.path.exists(p):
            print('%-24s %8.1f MB' % (name or 'total', du(p) / 1024 / 1024))
    print('build ok:', DIST)


if __name__ == '__main__':
    main()
