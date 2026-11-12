# -*- coding: utf-8 -*-
import json, hashlib, shutil, sys
sys.path.insert(0, '.')
from content_text import EVENTS, CARDS, CN_BANDS, WORLD_BANDS, CITIES, NOTES, REGIONS

meta = json.load(open('geoms_meta.json'))
zh = json.load(open('zh_names.json'))
extra = json.load(open('extra_meta.json'))
src = json.load(open('input/cliopatria.geojson'))
# 今地名表（places.py 生成）：[中文名, 经度, 纬度]
PLACES = [[n, float(lo), float(la)] for n, lo, la in (l.rstrip('\n').split('\t') for l in open('places.tsv', encoding='utf8') if l.strip())]
area = {}
for f in src['features']:
    p = f['properties']
    area[(p['Name'], p['FromYear'])] = p['Area']

# ---------- name overrides by year ----------
def zh_name(n, a):
    if n == 'Later Zhou': return '后周' if a > 0 else '东周'
    if n == 'Han': return '汉（汉王刘邦）' if a >= -206 else '韩'
    if n == 'Western Jin': return '东晋' if a >= 317 else '西晋'
    if n == 'Later Jin': return '后晋' if a >= 936 else '晋（沙陀李氏）'
    if n == 'Southern Wu': return '南唐' if a >= 947 else '吴（杨吴）／南唐'
    if n == 'Republic of China' and a >= 1950: return '台湾（中华民国政府）'
    if n == 'Republic of China' and a >= 1930: return '中华民国（国民政府）'
    if n == 'Wei' and a >= -208: return '魏（魏豹）'
    if n == 'Mongol Empire' and a >= 1260: return '蒙古帝国（元与诸汗国）'
    return zh[n]

# ---------- colors ----------
C = {}
def setc(names, col):
    for n in names.split('|'): C[n] = col
setc('Zhou Dynasty|Later Zhou', '#b4613f')
setc('Qin Dynasty|Qin', '#a9442f')
setc('Qi', '#4f9a9a'); setc('Chu', '#7f9e4e'); setc('Yan', '#6a8cab'); setc('Zhao', '#a39a55'); setc('Wei', '#9a78a6')
setc('Jin', '#8a86ac'); setc('Song', '#b0906a'); setc('Lu', '#7a9a6a'); setc('Zheng', '#a58ab0'); setc('Wey', '#6aa08a')
setc('Wu', '#4f86ad'); setc('Yue', '#6a9ab0'); setc('Zhongshan', '#929262'); setc('Cai', '#b08a8a'); setc('Chen', '#8aa07a')
setc('Han', '#b4868a')
setc('Han Dynasty|Xin Dynasty', '#c4553a')
setc('Cao Wei|Cao Cao', '#c2603e')
setc('Shu Han', '#86a052')
setc('Eastern Wu', '#4f8ab0')
setc('Western Jin', '#c45c40')
setc('Liu Song Dynasty|Southern Qi|Liang Dynasty|Chen Dynasty', '#c25a42')
setc('Northern Wei', '#c79a42')
setc('Eastern Wei|Northern Qi', '#bf8a3c')
setc('Western Wei|Northern Zhou', '#aca24c')
setc('Sui Dynasty', '#c8553c')
setc('Tang Dynasty', '#d2603f')
setc('Later Liang Dynasty|Later Tang|Later Han|Former Jin', '#c45c40')
setc('Liao Dynasty|Kara-Khitans', '#6f88b4')
setc('Western Xia', '#9c7cab')
setc('Northern Song|Southern Song', '#d06b43')
setc('Great Jin', '#cba443')
setc('Mongol Empire|Northern Yuan|Mongol Khanate|Tümed', '#8f6c4c')
setc('Yuan Dynasty', '#bb553e')
setc('Ming Dynasty|Southern Ming', '#d2563c')
setc('Later Jin Dynasty', '#cf9a3c')
setc('Qing Dynasty', '#d78c3c')
setc('Taiping Heavenly Kingdom', '#c9b04b')
setc('Republic of China|Empire of China', '#bd5046')
setc('Kuomintang', '#4a74b4')
setc("People's Republic of China|Communist Party of China|Chinese Communists", '#d24b3a')
setc('Tibetan Empire|Tibetans|Tibet', '#8b9c5c')
setc('Nanzhao|Kingdom of Dali', '#a9805c')
setc('Xiongnu|Southern Xiongnu', '#9d8862')
setc('Xianbei', '#8f9c6b')
setc('Rouran Khaganate', '#8a8a5c')
setc('Göktürk Khaganate|Eastern Göktürks|Western Göktürks|Turks|Türgesh', '#a68c5c')
setc('Uyghur Khaganate|Qocho Kingdom|Ganzhou Kingdom', '#7aa38c')
setc('Dzungar Khanate|Four Oirats|Oirat Confederation|Khoshut Khanate', '#8e7ca0')
setc('Gojoseon|Goguryeo|Silla|Unified Silla|Goryeo|Joseon|Korean Empire|Baekje|Balhae|Republic of Korea|Democratic People\'s Republic of Korea', '#4f9c97')
setc('Asuka Japan|Nara Japan|Heian Japan|Kamakura Shogunate|Ashikaga Shogunate|Warring States Japan|Tokugawa Shogunate|Kenmu Restoration|Japan', '#a9718f')
setc('Empire of Japan', '#b25c7c')
setc('Ngô Dynasty|Đại Việt|Lê Dynasty|Nguyễn dynasty|Socialist Republic of Vietnam', '#7ca25c')
setc('Roman Kingdom|Roman Republic|Roman Empire|Western Roman Empire|Eastern Roman Empire|Byzantine Empire', '#9067aa')
setc('Achaemenid Empire|Parthian Empire|Sasanian Empire|Safavid Dynasty|Afsharid Iran|Qajar Dynasty|Pahlavi Dynasty|Islamic Republic of Iran', '#3f9b8e')
setc('Rashidun Caliphate|Umayyad Caliphate|Abbasid Caliphate|Fatimid Caliphate', '#5c9c5c')
setc('Ottoman Empire|Republic of Turkey', '#4f9272')
setc('Maurya Empire|Gupta Empire|Mughal Empire|Mamluk Dynasty|Khalji Dynasty|Tughlaq Dynasty|Lodi Dynasty|Sayyid Dynasty|Republic of India', '#c9a248')
setc('Grand Principality of Moscow|Tsardom of Russia|Russian Empire|Russian Federation|Russian Republic', '#6a8cb8')
setc('Union of Soviet Socialist Republics|Republics of the Soviet Union', '#a0536f')
setc('British Empire|British Colonial Empire|British Raj|British Africa|Kingdom of Great Britain|Kingdom of England|British East Africa|British Gold Coast|British Cape Colony|British Ceylon', '#c97c97')
setc('Kingdom of France|French First Republic|First French Empire|French Third Republic|French Fourth Republic|French Fifth Republic|French Africa|French Indochina|Second French Empire|Bourbon Kingdom of France|French Second Republic|French Directory|French Consulate|Vichy France', '#5c80c4')
setc('Spanish Empire|Kingdom of Spain|Crown of Castile', '#cbaa3c')
setc('Portuguese Empire|Kingdom of Portugal|Portuguese Colonies', '#4f9c80')
setc('Dutch Republic|Netherlands|Dutch East Indies', '#d28c47')
setc('United States of America', '#6090c2')
setc('Holy Roman Empire|Kingdom of Germany|East Franks', '#8e8aa8')
setc('German Empire|Weimar Republic|Nazi Germany|Federated Republic of Germany', '#80809c')
setc('Mongolian People\'s Republic|Mongolia|Great Mongol State', '#9a7a5a')
PAL = ['#b07c5c','#7c9c6c','#6c8ca2','#9c7ca2','#a29c5c','#5c9c9c','#a2826c','#8ca27c',
       '#7c8cb2','#b28c8c','#6ca28c','#a28cb2','#929262','#6c9cb2','#b2946a','#86a2a0']
def color(n):
    if n in C: return C[n]
    h = int(hashlib.md5(n.encode()).hexdigest()[:8], 16)
    return PAL[h % len(PAL)]

# ---------- names table ----------
names = []; nidx = {}
def name_id(n, a):
    z = zh_name(n, a)
    key = (n, z)
    if key not in nidx:
        nidx[key] = len(names)
        rec = {'en': n, 'zh': z, 'c': ('#c4553a' if z.startswith('汉（汉王') else color(n))}
        w = extra['wiki'].get(n)
        if w: rec['w'] = w
        if n in NOTES: rec['note'] = NOTES[n]
        names.append(rec)
    return nidx[key]

# aggregates (membership) in Chinese
def agg_zh(a):
    s = a.strip('()')
    def b(x): return zh.get(x, x)
    import re
    m = re.match(r'Allegiance of (.+) to (.+)$', s)
    if m: return f'{b(m.group(1))}臣属于{b(m.group(2))}'
    m = re.match(r'Vassalage of (.+) to (.+)$', s)
    if m: return f'{b(m.group(1))}为{b(m.group(2))}藩属'
    m = re.match(r'Alliance between (.+) and (.+)$', s)
    if m: return f'{b(m.group(1))}与{b(m.group(2))}结盟'
    m = re.match(r'Personal union of (.+) with (.+)$', s)
    if m: return f'{b(m.group(1))}与{b(m.group(2))}共主'
    special = {'Spring and Autumn States':'春秋列国','Warring States China':'战国诸国','Eighteen Kingdoms':'楚汉之际十八诸侯国',
               'Five Dynasties and Ten Kingdoms':'五代十国','Mahajanapadas':'印度十六大国','Phoenician Empire':'腓尼基城邦与殖民地',
               'Macedonian Empire':'马其顿帝国','Taifas of Iberia':'伊比利亚泰法诸国','Brythonic Kingdoms':'不列颠人诸王国',
               'Polish-Lithuania Kingdom':'波兰-立陶宛','Commonwealth of Nations':'英联邦','Delhi Sultanate':'德里苏丹国',
               'British Empire':'大英帝国（含殖民地）','Spanish Empire':'西班牙帝国（含殖民地）','Portuguese Empire':'葡萄牙帝国（含殖民地）',
               'Chenla':'真腊','Russian Federation':'俄罗斯联邦','Netherlands':'荷兰（含海外领地）'}
    if s in special: return special[s]
    return zh.get(s, s)

rows = []
mem = extra['mem']
aggnames = []; aidx = {}
for n, a, b, g in meta['rows']:
    ni = name_id(n, a)
    ar = area.get((n, a), 0)
    m = mem.get(f'{n}@{a}')
    mi = -1
    if m:
        z = agg_zh(m)
        if z not in aidx: aidx[z] = len(aggnames); aggnames.append(z)
        mi = aidx[z]
    rows.append([ni, a, b, g, round(ar / 1000), mi])

# ---------- chronology ----------
CN_NUM = '〇一二三四五六七八九'
def cnum(k):
    if k == 1: return '元'
    if k < 10: return CN_NUM[k]
    if k < 20: return '十' + (CN_NUM[k % 10] if k % 10 else '')
    if k < 100: return CN_NUM[k // 10] + '十' + (CN_NUM[k % 10] if k % 10 else '')
    return str(k)
def nian(k): return cnum(k) + '年'
GAN = '甲乙丙丁戊己庚辛壬癸'; ZHI = '子丑寅卯辰巳午未申酉戌亥'
def ganzhi(y):
    a = y + 1 if y < 0 else y
    i = (a - 4) % 60
    return GAN[i % 10] + ZHI[i % 12]

# pre-140 BCE reign tables (BCE years as positive numbers): (start, end, label)
ZHOU = [(827,782,'周宣王'),(781,771,'周幽王'),(770,720,'周平王'),(719,697,'周桓王'),(696,682,'周庄王'),
        (681,677,'周釐王'),(676,652,'周惠王'),(651,619,'周襄王'),(618,613,'周顷王'),(612,607,'周匡王'),
        (606,586,'周定王'),(585,572,'周简王'),(571,545,'周灵王'),(544,520,'周景王'),(519,476,'周敬王'),
        (475,469,'周元王'),(468,441,'周贞定王'),(440,426,'周考王'),(425,402,'周威烈王'),(401,376,'周安王'),
        (375,369,'周烈王'),(368,321,'周显王'),(320,315,'周慎靓王'),(314,256,'周赧王')]
LU = [(722,712,'鲁隐公'),(711,694,'鲁桓公'),(693,662,'鲁庄公'),(661,660,'鲁闵公'),(659,627,'鲁僖公'),
      (626,609,'鲁文公'),(608,591,'鲁宣公'),(590,573,'鲁成公'),(572,542,'鲁襄公'),(541,510,'鲁昭公'),
      (509,495,'鲁定公'),(494,481,'鲁哀公')]
QIN = [(384,362,'秦献公'),(361,338,'秦孝公'),(337,325,'秦惠文君'),(324,311,'秦惠文王更元'),(310,307,'秦武王'),
       (306,251,'秦昭襄王'),(250,250,'秦孝文王'),(249,247,'秦庄襄王'),(246,222,'秦王政'),(221,210,'秦始皇'),
       (209,207,'秦二世')]
HAN0 = [(206,195,'汉高祖'),(194,188,'汉惠帝'),(187,180,'汉高后'),(179,164,'汉文帝前元'),(163,157,'汉文帝后元'),
        (156,150,'汉景帝前元'),(149,144,'汉景帝中元'),(143,141,'汉景帝后元')]
def reign(tbl, bce, base=None):
    for s, e, lab in tbl:
        if e <= bce <= s:
            if lab == '秦始皇': return lab + nian(246 - bce + 1)
            return lab + nian(s - bce + 1)
    return None

chron_src = json.load(open('chronology.json'))
eras = []
for e in chron_src['eras']:
    d = e['dynastyName']; nm = e['name']
    if d == '中华民国' and nm == '中华民国': continue
    if d == '周': d = '唐' if nm in ('文明','光宅','垂拱','永昌','载初') else '武周'
    if nm == '永昌' and e['startYear'] == 689: e = dict(e, endYear=689)
    if d == '清' and e['startYear'] < 1636: d = '后金'
    if d == '元' and e['startYear'] < 1260: d = '大蒙古国'
    eras.append((d, nm, e['startYear'], e['endYear'], e['id']))
DISP = {'三国魏':'魏','三国蜀':'蜀','三国吴':'吴','刘宋':'宋','南齐':'齐','南梁':'梁','杨吴':'吴','闽国':'闽','中华民国':'中华民国'}
MAIN = {'汉','新','三国魏','三国蜀','三国吴','西晋','东晋','北魏','刘宋','南齐','南梁','陈','东魏','西魏','北齐','北周',
        '隋','唐','武周','后梁','后唐','后晋','后汉','后周','宋','辽','金','西夏','大蒙古国','元','明','后金','清','南明','中华民国'}
ORDER = ['汉','新','三国魏','三国蜀','三国吴','西晋','东晋','刘宋','南齐','南梁','陈','北魏','东魏','西魏','北齐','北周',
         '隋','唐','武周','后梁','后唐','后晋','后汉','后周','宋','辽','西夏','金','大蒙古国','元','明','后金','清','南明','中华民国']
def era_line(y):
    by = {}
    for d, nm, s, e, i in eras:
        if s <= y <= e:
            by.setdefault(d, []).append((s, i, nm))
    main = []; other = []
    for d, lst in by.items():
        lst.sort()
        dn = DISP.get(d, d)
        if d == '中华民国':
            txt = '民国' + nian(y - 1911)
        else:
            txt = dn + '→'.join(nm + nian(y - s + 1) for s, i, nm in lst)
        (main if d in MAIN else other).append((ORDER.index(d) if d in ORDER else 99, txt))
    main.sort(); other.sort()
    return [t for _, t in main], [t for _, t in other]

def period(y, bands):
    for a, b, n in bands:
        if a <= y <= b: return n
    return ''

chron = {}
for y in range(-800, 2025):
    if y == 0: continue
    main = []; other = []
    if y < 0:
        bce = -y
        if bce >= 256:
            r = reign(ZHOU, bce)
            if r: main.append(r)
            if 481 <= bce <= 722:
                l = reign(LU, bce)
                if l: other.append(l)
            if 257 <= bce <= 384:
                q = reign(QIN, bce)
                if q: other.append(q)
            if bce == 256:
                other.append(reign(QIN, bce))
        if 207 <= bce <= 255:
            q = reign(QIN, bce)
            if q:
                if bce == 221: q = '秦王政二十六年（称始皇帝）'
                main.append(q)
            if bce == 207: main.append('秦王子婴')
        if 141 <= bce <= 206:
            h = reign(HAN0, bce)
            if h: main.append(h)
            if 202 <= bce <= 206: other.append('西楚霸王项羽' + nian(206 - bce + 1))
        if bce <= 140:
            m, o = era_line(y); main += m; other += o
    else:
        if y <= 1949:
            m, o = era_line(y); main += m; other += o
        if y == 1949:
            main.append('中华人民共和国成立')
    chron[y] = {'m': main, 'o': other, 'g': ganzhi(y), 'p': period(y, CN_BANDS), 'w': period(y, WORLD_BANDS)}

# spot checks
for y in [-800,-722,-551,-475,-260,-256,-221,-210,-207,-206,-202,-180,-141,-140,9,23,25,220,263,383,589,690,755,907,960,1004,1127,1279,1368,1644,1662,1912,1949,2024]:
    c = chron[y]; print(y, c['p'], c['g'], ' · '.join(c['m']), '| 并立:', ' · '.join(c['o'][:6]))

data = {
    'Q': meta['Q'], 'offs': meta['offs'], 'lab': meta['labels'], 'rows': rows, 'names': names, 'aggs': aggnames,
    'chron': {str(k): v for k, v in chron.items()},
    'events': [list(e) for e in EVENTS], 'cards': CARDS, 'cnb': CN_BANDS, 'wdb': WORLD_BANDS,
    'cities': [[lo, la, segs, t] for lo, la, segs, t in CITIES], 'regions': REGIONS,
    'places': PLACES,
}
json.dump(data, open('out/data.json', 'w'), ensure_ascii=False, separators=(',', ':'))
shutil.copy('geoms.bin', 'out/geo.bin')
import os
print('data.json', os.path.getsize('out/data.json'), 'names', len(names), 'aggs', len(aggnames), 'rows', len(rows))
