# -*- coding: utf-8 -*-
"""今地名表：从 Natural Earth 的 populated places 生成 places.tsv（中文名、经度、纬度）。
用于页面里的搜索（输入“郑州”直接飞过去）、“家乡三千年”选地点，以及“今某地附近”的提示。

输入：input/natural-earth/ne_10m_populated_places.geojson
依赖：pip install opencc-python-reimplemented   （把个别繁体译名转成简体）
收录：中国全部条目；其他国家只收首都和人口 100 万以上的城市。只取名称和坐标，不含国别。
"""
import json, re
from opencc import OpenCC

cc = OpenCC('t2s')
src = json.load(open('input/natural-earth/ne_10m_populated_places.geojson', encoding='utf8'))
CN = ('CHN', 'TWN', 'HKG', 'MAC')

# Natural Earth 的中文名取自 Wikidata，个别条目链接错了或用了非大陆通行译名，在此改正。键是英文名。
FIX_CN = {
    'Hangu': '汉沽', 'Ninde': '宁德', 'Bose': '百色', 'Nancha': '南岔', 'Hami': '哈密', 'Tengchong': '腾冲',
    'Puqi': '赤壁', 'Jyekundo': '玉树', 'Zicheng': '枝城', 'Orongen Zizhiqi': '鄂伦春旗',
    'Jinxi': '葫芦岛', 'Changping': '昌平', 'Jianmen': '天门', 'Anxi': '瓜州', 'Yishan': '宜州', 'Fulin': '汉源',
    'Jingdezhen': '景德镇', 'Simao': '普洱',
}
FIX_CN_AT = {('Jining', 'Nei Mongol'): '集宁', ('Dali', 'Shaanxi'): '大荔',
             ('Wuchuan', 'Nei Mongol'): '武川', ('Wuyuan', 'Nei Mongol'): '五原'}
FIX_WORLD = {
    '嘉柏隆里': '哈博罗内', '培亚': '普拉亚', '圣荷西': '圣何塞', '杜塞道夫': '杜塞尔多夫', '美因河畔法兰克福': '法兰克福',
    '吉布地': '吉布提', '圣多明哥': '圣多明各', '亚历山大港': '亚历山大', '班竹': '班珠尔', '瓜地马拉': '危地马拉城',
    '瓦兰希': '瓦拉纳西', '科伊巴拓雷': '哥印拜陀', '阿么达巴德': '艾哈迈达巴德', '西菈子': '设拉子', '京斯敦': '金斯敦',
    '努尔苏丹': '阿斯塔纳', '蔚山广域': '蔚山', '仁川广域': '仁川', '大田广域': '大田', '光州广域': '光州',
    '马拿瓜': '马那瓜', '奥克兰都会区': '奥克兰', '南浦特别': '南浦', '吉佳利': '基加利', '利雅德': '利雅得',
    '三兰港': '达累斯萨拉姆', '欧文': '尔湾', '维珍尼亚海滩': '弗吉尼亚海滩', '沙加缅度': '萨克拉门托',
    '克里夫兰': '克利夫兰', '水牛城': '布法罗', '华盛顿哥伦比亚特区': '华盛顿', '胡志明': '胡志明市',
    '伊莉莎白港': '伊丽莎白港', '乔治': '乔治市', '圣地牙哥': None,   # None = 不收（与智利圣地亚哥重名）
}

rows = []
for f in src['features']:
    p = f['properties']
    china = p['ADM0_A3'] in CN
    if not china and not (p['ADM0CAP'] == 1 or p['POP_MAX'] >= 1_000_000): continue
    zh = cc.convert(p['NAME_ZH'] or '').strip()
    if china:
        fixed = FIX_CN_AT.get((p['NAME'], p['ADM1NAME']), FIX_CN.get(p['NAME']))
        if fixed: zh = fixed
        elif len(zh) > 2: zh = re.sub(r'(特别行政区|矿区|街道|市|区|县|镇)$', '', zh)
    else:
        zh = FIX_WORLD.get(zh, zh)
    if not zh or re.search(r'[A-Za-z]', zh): continue
    rows.append((zh, round(p['LONGITUDE'], 2), round(p['LATITUDE'], 2), p['POP_MAX'], china))

# 同名且相距不到 1° 的只留人口多的一个
rows.sort(key=lambda r: -r[3])
keep = []
for r in rows:
    if any(k[0] == r[0] and abs(k[1] - r[1]) < 1 and abs(k[2] - r[2]) < 1 for k in keep): continue
    keep.append(r)
keep.sort(key=lambda r: (not r[4], -r[3]))   # 中国在前，各自按人口从多到少
with open('places.tsv', 'w', encoding='utf8') as o:
    for zh, lo, la, _, _ in keep: o.write(f'{zh}\t{lo:.2f}\t{la:.2f}\n')
print('places.tsv', len(keep), '条；其中中国', sum(1 for r in keep if r[4]))
