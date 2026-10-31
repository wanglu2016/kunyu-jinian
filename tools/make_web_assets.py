# -*- coding: utf-8 -*-
"""Last step: turn tools/out/* into the script files the page loads (../assets/*.js).
Data is wrapped in <script>-loadable files so the page also works when index.html is opened straight from disk."""
import base64

data = open('out/data.json', encoding='utf8').read()
open('../assets/data.js', 'w', encoding='utf8').write('window.__KUNYU_DATA=' + data + ';\n')
geo = base64.b64encode(open('out/geo.bin', 'rb').read()).decode()
open('../assets/geo.js', 'w').write('window.__KUNYU_GEO="' + geo + '";\n')
b = base64.b64encode(open('out/base.jpg', 'rb').read()).decode()
l = base64.b64encode(open('out/land.png', 'rb').read()).decode()
open('../assets/textures.js', 'w').write(
    'window.__KUNYU_TEX={base:"data:image/jpeg;base64,' + b + '",land:"data:image/png;base64,' + l + '"};\n')
print('assets written')
