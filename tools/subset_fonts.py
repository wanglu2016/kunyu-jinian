# -*- coding: utf-8 -*-
"""按页面实际用到的字裁剪字体，写入 ../assets/fonts/*.woff2。
页面文字或数据（事件、地名）有增改后需要重跑，否则新出现的字会落到系统字体上，同一行里字形不一致。

输入：input/fonts/ 下的 6 个原始字体（Noto CJK 的 SubsetOTF/SC）：
  NotoSansSC-Regular.otf  NotoSansSC-Medium.otf  NotoSansSC-Bold.otf
  NotoSerifSC-Medium.otf  NotoSerifSC-Bold.otf   NotoSerifSC-Black.otf
  来源 https://github.com/notofonts/noto-cjk （Sans 2.004 / Serif 2.003）
依赖：pip install fonttools brotli
"""
import glob, os
from fontTools import subset
from fontTools.ttLib import TTFont

SRC = ['../index.html', '../video.html', '../assets/data.js']
chars = set(range(0x20, 0x7f))
for f in SRC:
    chars |= {ord(c) for c in open(f, encoding='utf8').read() if ord(c) >= 0xa0}
# 常用标点、数字符号，以及手写输入时容易碰到的字符
chars |= {ord(c) for c in '，。、；：？！“”‘’（）《》〈〉【】—…·～－＋×÷°→←↑↓↗％‰＃＆＊０１２３４５６７８９〇零一二三四五六七八九十百千万亿年月日时分秒'}
# 已有子集里的字一个不丢
for f in glob.glob('../assets/fonts/*.woff2'):
    chars |= set(TTFont(f).getBestCmap().keys())

for name in ['NotoSansSC-Regular', 'NotoSansSC-Medium', 'NotoSansSC-Bold', 'NotoSerifSC-Medium', 'NotoSerifSC-Bold', 'NotoSerifSC-Black']:
    font = TTFont(f'input/fonts/{name}.otf')
    opt = subset.Options(); opt.flavor = 'woff2'; opt.layout_features = ['*']; opt.name_IDs = ['*']; opt.notdef_outline = True
    s = subset.Subsetter(opt); s.populate(unicodes=sorted(chars)); s.subset(font)
    out = f'../assets/fonts/{name}.woff2'; font.flavor = 'woff2'; font.save(out)
    print(name, len(font.getBestCmap()), 'chars', os.path.getsize(out) // 1024, 'KB')
