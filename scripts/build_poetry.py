# -*- coding: utf-8 -*-
"""从 chinese-poetry 抽取中小学常用古诗文，生成 data/poetry.json。
- 蒙学、诗经、论语、唐诗、宋词、元曲
- 简繁统一为简体（OpenCC t2s）
- 唐诗/宋词/元曲按“名篇清单”挑选，避免把 5.5 万首全量塞进页面
"""
import json
import os
import re
import glob
import sys
from opencc import OpenCC

CC = OpenCC('t2s')


def s(text):
    return CC.convert(str(text or ''))


def norm_title(t):
    return re.sub(r'[\s·・]+', '', str(t or ''))


# ---------- 唐诗：题目 + 作者 ----------
TANG = [
    ("静夜思", "李白"), ("春晓", "孟浩然"), ("登鹳雀楼", "王之涣"),
    ("望庐山瀑布", "李白"), ("早发白帝城", "李白"), ("送元二使安西", "王维"),
    ("九月九日忆山东兄弟", "王维"), ("咏鹅", "骆宾王"), ("悯农", "李绅"),
    ("江雪", "柳宗元"), ("绝句", "杜甫"), ("山行", "杜牧"),
    ("枫桥夜泊", "张继"), ("黄鹤楼送孟浩然之广陵", "李白"), ("赠汪伦", "李白"),
    ("回乡偶书", "贺知章"), ("凉州词", "王之涣"), ("出塞", "王昌龄"),
    ("鹿柴", "王维"), ("竹里馆", "王维"), ("相思", "王维"),
    ("春夜喜雨", "杜甫"), ("望岳", "杜甫"), ("春望", "杜甫"),
    ("茅屋为秋风所破歌", "杜甫"), ("登高", "杜甫"), ("蜀道难", "李白"),
    ("将进酒", "李白"), ("行路难", "李白"), ("梦游天姥吟留别", "李白"),
    ("琵琶行", "白居易"), ("长恨歌", "白居易"), ("卖炭翁", "白居易"),
    ("钱塘湖春行", "白居易"), ("雁门太守行", "李贺"), ("赤壁", "杜牧"),
    ("泊秦淮", "杜牧"), ("夜雨寄北", "李商隐"), ("无题", "李商隐"),
    ("锦瑟", "李商隐"), ("乐游原", "李商隐"), ("过故人庄", "孟浩然"),
    ("望洞庭湖赠张丞相", "孟浩然"), ("使至塞上", "王维"), ("送杜少府之任蜀州", "王勃"),
    ("次北固山下", "王湾"), ("题破山寺后禅院", "常建"), ("闻王昌龄左迁龙标遥有此寄", "李白"),
    ("峨眉山月歌", "李白"), ("春夜洛城闻笛", "李白"), ("逢入京使", "岑参"),
    ("晚春", "韩愈"), ("登幽州台歌", "陈子昂"), ("竹枝词", "刘禹锡"),
    ("乌衣巷", "刘禹锡"), ("秋词", "刘禹锡"), ("酬乐天扬州初逢席上见赠", "刘禹锡"),
    ("观刈麦", "白居易"), ("寻隐者不遇", "贾岛"), ("游子吟", "孟郊"),
    ("寒食", "韩翃"), ("滁州西涧", "韦应物"), ("江南逢李龟年", "杜甫"),
    ("月夜", "刘方平"), ("春雪", "韩愈"), ("早春呈水部张十八员外", "韩愈"),
    ("白雪歌送武判官归京", "岑参"), ("别董大", "高适"), ("塞下曲", "卢纶"),
    ("小儿垂钓", "胡令能"), ("池上", "白居易"), ("赋得古原草送别", "白居易"),
    ("暮江吟", "白居易"), ("忆江南", "白居易"), ("浪淘沙", "刘禹锡"),
    ("望天门山", "李白"), ("独坐敬亭山", "李白"), ("秋浦歌", "李白"),
    ("忆江南", "白居易"),
]

# ---------- 宋诗：题目 + 作者 ----------
SONG_SHI = [
    ("题西林壁", "苏轼"), ("饮湖上初晴后雨", "苏轼"), ("惠崇春江晚景", "苏轼"),
    ("赠刘景文", "苏轼"), ("六月二十七日望湖楼醉书", "苏轼"),
    ("示儿", "陆游"), ("游山西村", "陆游"), ("秋夜将晓出篱门迎凉有感", "陆游"),
    ("十一月四日风雨大作", "陆游"), ("冬夜读书示子聿", "陆游"),
    ("四时田园杂兴", "范成大"), ("小池", "杨万里"), ("晓出净慈寺送林子方", "杨万里"),
    ("宿新市徐公店", "杨万里"), ("舟过安仁", "杨万里"), ("稚子弄冰", "杨万里"),
    ("春日", "朱熹"), ("观书有感", "朱熹"), ("过零丁洋", "文天祥"),
    ("题临安邸", "林升"), ("泊船瓜洲", "王安石"), ("梅花", "王安石"),
    ("元日", "王安石"), ("登飞来峰", "王安石"), ("书湖阴先生壁", "王安石"),
    ("山园小梅", "林逋"), ("村行", "王禹偁"), ("鲁山山行", "梅尧臣"),
    ("画眉鸟", "欧阳修"), ("戏答元珍", "欧阳修"), ("淮中晚泊犊头", "苏舜钦"),
    ("城南", "曾巩"), ("雨后池上", "刘攽"), ("春游湖", "徐俯"),
    ("病牛", "李纲"), ("夏日绝句", "李清照"), ("三衢道中", "曾几"),
    ("雨晴", "陈与义"), ("游园不值", "叶绍翁"), ("约客", "赵师秀"),
    ("乡村四月", "翁卷"), ("雪梅", "卢梅坡"), ("扬子江", "文天祥"),
]

# ---------- 宋词：词牌 + 首句片段 + 作者 ----------
SONG = [
    ("水调歌头", "明月几时有", "苏轼"),
    ("念奴娇", "大江东去", "苏轼"),
    ("江城子", "老夫聊发少年狂", "苏轼"),
    ("江城子", "十年生死两茫茫", "苏轼"),
    ("定风波", "莫听穿林打叶声", "苏轼"),
    ("卜算子", "缺月挂疏桐", "苏轼"),
    ("浣溪沙", "簌簌衣巾落枣花", "苏轼"),
    ("如梦令", "常记溪亭日暮", "李清照"),
    ("如梦令", "昨夜雨疏风骤", "李清照"),
    ("醉花阴", "薄雾浓云愁永昼", "李清照"),
    ("声声慢", "寻寻觅觅", "李清照"),
    ("武陵春", "风住尘香花已尽", "李清照"),
    ("一剪梅", "红藕香残玉簟秋", "李清照"),
    ("破阵子", "醉里挑灯看剑", "辛弃疾"),
    ("西江月", "明月别枝惊鹊", "辛弃疾"),
    ("永遇乐", "千古江山", "辛弃疾"),
    ("青玉案", "东风夜放花千树", "辛弃疾"),
    ("丑奴儿", "少年不识愁滋味", "辛弃疾"),
    ("南乡子", "何处望神州", "辛弃疾"),
    ("满江红", "怒发冲冠", "岳飞"),
    ("雨霖铃", "寒蝉凄切", "柳永"),
    ("渔家傲", "塞下秋来风景异", "范仲淹"),
    ("浣溪沙", "一曲新词酒一杯", "晏殊"),
    ("蝶恋花", "庭院深深深几许", "欧阳修"),
    ("鹊桥仙", "纤云弄巧", "秦观"),
    ("钗头凤", "红酥手", "陆游"),
    ("卜算子", "驿外断桥边", "陆游"),
    ("扬州慢", "淮左名都", "姜夔"),
    ("苏幕遮", "燎沉香", "周邦彦"),
    ("虞美人", "春花秋月何时了", "李煜"),
    ("相见欢", "无言独上西楼", "李煜"),
    ("浪淘沙令", "帘外雨潺潺", "李煜"),
    ("临江仙", "梦后楼台高锁", "晏几道"),
    ("青玉案", "凌波不过横塘路", "贺铸"),
    ("念奴娇", "洞庭青草", "张孝祥"),
    ("虞美人", "少年听雨歌楼上", "蒋捷"),
]

# ---------- 元曲：题目片段 + 作者 ----------
YUAN = [
    ("天净沙", "秋思", "马致远"),
    ("天净沙", "春", "白朴"),
    ("天净沙", "夏", "白朴"),
    ("天净沙", "秋", "白朴"),
    ("天净沙", "冬", "白朴"),
    ("山坡羊", "潼关怀古", "张养浩"),
    ("山坡羊", "骊山怀古", "张养浩"),
    ("水仙子", "夜雨", "徐再思"),
    ("折桂令", "春情", "徐再思"),
    ("四块玉", "别情", "关汉卿"),
    ("沉醉东风", "秋景", "关汉卿"),
    ("寄生草", "饮", "白朴"),
    ("阳春曲", "知几", "白朴"),
    ("清江引", "野兴", "马致远"),
    ("寿阳曲", "远浦帆归", "马致远"),
]


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def add(out, cat, title, author, dynasty, paragraphs, note=''):
    title = s(title).strip()
    author = s(author).strip()
    paragraphs = [s(p).strip() for p in paragraphs if s(p).strip()]
    if not title or not paragraphs:
        return
    key = (cat, norm_title(title), author, paragraphs[0][:20])
    if key in out['seen']:
        return
    out['seen'].add(key)
    out['poems'].append({
        'id': '%s-%d' % (cat.lower(), len(out['poems'])),
        'cat': cat,
        'title': title,
        'author': author,
        'dynasty': dynasty,
        'paragraphs': paragraphs,
        'note': note,
    })


def build(src, dst):
    out = {'categories': ['蒙学', '诗经', '论语', '唐诗', '宋诗', '宋词', '元曲'], 'poems': [], 'seen': set()}

    # 蒙学
    meng = [
        ('蒙学/sanzijing-new.json', '三字经', '王应麟', '宋'),
        ('蒙学/dizigui.json', '弟子规', '李毓秀', '清'),
        ('蒙学/qianziwen.json', '千字文', '周兴嗣', '南朝'),
        ('蒙学/baijiaxing.json', '百家姓', '佚名', '北宋'),
        ('蒙学/shenglvqimeng.json', '声律启蒙', '车万育', '清'),
    ]
    for rel, title, author, dyn in meng:
        path = os.path.join(src, rel)
        if not os.path.exists(path):
            continue
        obj = load_json(path)

        def flatten(node):
            result = []
            if isinstance(node, dict):
                if node.get('paragraphs'):
                    result.extend(node.get('paragraphs', []))
                for v in node.values():
                    if isinstance(v, list) and v and isinstance(v[0], dict):
                        result.extend(flatten(v))
            elif isinstance(node, list):
                for item in node:
                    result.extend(flatten(item))
            return result

        add(out, '蒙学', obj.get('title', title), obj.get('author', author), dyn, flatten(obj))

    # 诗经
    shijing_path = os.path.join(src, '诗经/shijing.json')
    if os.path.exists(shijing_path):
        for item in load_json(shijing_path):
            note = ' · '.join([x for x in [item.get('chapter'), item.get('section')] if x])
            add(out, '诗经', item.get('title', ''), '佚名', '先秦', item.get('content', []), note)

    # 论语
    lunyu_path = os.path.join(src, '论语/lunyu.json')
    if os.path.exists(lunyu_path):
        for item in load_json(lunyu_path):
            add(out, '论语', '论语·' + item.get('chapter', ''), '孔子及弟子', '先秦', item.get('paragraphs', []))

    # 唐诗索引
    tang = []
    for f in sorted(glob.glob(os.path.join(src, '全唐诗/poet.tang.*.json'))):
        tang.extend(load_json(f))
    tang_idx = {}
    for p in tang:
        tang_idx.setdefault(norm_title(s(p.get('title', ''))), []).append(p)

    used = set()
    for title, author in TANG:
        key = norm_title(title)
        candidates = list(tang_idx.get(key, []))
        # 允许“悯农二首”“辋川集 鹿柴”这类前缀/包含匹配；先按作者筛选，避免抓到同名异作者
        for k, v in tang_idx.items():
            if k != key and (k.startswith(key) or key in k):
                candidates.extend(v)
        if author:
            candidates = [p for p in candidates if author in s(p.get('author', ''))]
        if not candidates:
            print('  [唐诗未匹配]', title, author, file=sys.stderr)
            continue
        chosen = candidates[0]
        k = id(chosen)
        if k in used:
            continue
        used.add(k)
        add(out, '唐诗', title, chosen.get('author', author), '唐', chosen.get('paragraphs', []))

    # 宋诗索引
    song_shi = []
    for f in sorted(glob.glob(os.path.join(src, '全唐诗/poet.song.*.json'))):
        song_shi.extend(load_json(f))
    song_shi_idx = {}
    for p in song_shi:
        song_shi_idx.setdefault(norm_title(s(p.get('title', ''))), []).append(p)

    used = set()
    for title, author in SONG_SHI:
        key = norm_title(title)
        candidates = list(song_shi_idx.get(key, []))
        for k, v in song_shi_idx.items():
            if k != key and (k.startswith(key) or key in k):
                candidates.extend(v)
        if author:
            candidates = [p for p in candidates if author in s(p.get('author', ''))]
        if not candidates:
            print('  [宋诗未匹配]', title, author, file=sys.stderr)
            continue
        chosen = candidates[0]
        k = id(chosen)
        if k in used:
            continue
        used.add(k)
        add(out, '宋诗', title, chosen.get('author', author), '宋', chosen.get('paragraphs', []))

    # 宋词索引
    song = []
    for f in sorted(glob.glob(os.path.join(src, '宋词/ci.song.*.json'))):
        song.extend(load_json(f))

    used = set()
    for rhythmic, first, author in SONG:
        chosen = None
        for p in song:
            if rhythmic not in s(p.get('rhythmic', '')):
                continue
            if author not in s(p.get('author', '')):
                continue
            body = ' '.join(p.get('paragraphs', []))
            if first and first not in s(body):
                continue
            chosen = p
            break
        if chosen is None:
            print('  [宋词未匹配]', rhythmic, first, author, file=sys.stderr)
            continue
        k = id(chosen)
        if k in used:
            continue
        used.add(k)
        title = s(chosen.get('rhythmic', rhythmic)).split('・')[0] + '·' + s(first)
        add(out, '宋词', title, chosen.get('author', author), '宋', chosen.get('paragraphs', []))

    # 元曲
    yuan_path = os.path.join(src, '元曲/yuanqu.json')
    if os.path.exists(yuan_path):
        yuan = load_json(yuan_path)
        used = set()
        for title_part, subtitle, author in YUAN:
            chosen = None
            for p in yuan:
                t = s(p.get('title', ''))
                if title_part not in t:
                    continue
                if author and author not in s(p.get('author', '')):
                    continue
                if subtitle and subtitle not in t:
                    continue
                chosen = p
                break
            if chosen is None:
                print('  [元曲未匹配]', title_part, subtitle, author, file=sys.stderr)
                continue
            k = id(chosen)
            if k in used:
                continue
            used.add(k)
            add(out, '元曲', title_part + ('·' + subtitle if subtitle else ''), chosen.get('author', author), '元', chosen.get('paragraphs', []))

    out['poems'].sort(key=lambda x: (out['categories'].index(x['cat']), x['title']))
    for i, p in enumerate(out['poems']):
        p['id'] = '%s-%d' % (p['cat'], i)
    meta = {'count': len(out['poems']), 'categories': out['categories'], 'generated': '2026-11-24'}
    result = {'meta': meta, 'categories': out['categories'], 'poems': out['poems']}

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, separators=(',', ':'))
    print('poetry:', len(out['poems']), 'poems ->', dst)
    from collections import Counter
    print('categories:', dict(Counter(p['cat'] for p in out['poems'])))
    return result


if __name__ == '__main__':
    src = sys.argv[1]
    dst = sys.argv[2]
    build(src, dst)
