# 数据处理流程

网页本身不需要构建，`assets/` 里已经是处理好的数据。只有想重新生成数据（比如修改中文译名、事件或配色）时才需要这里的脚本。

需要 Python 3.10+，以及 `pip install shapely numpy pillow scipy`。

## 准备输入文件（放进 `tools/input/`）

| 文件 | 来源 |
|---|---|
| `cliopatria.geojson` | [Cliopatria](https://github.com/Seshat-Global-History-Databank/cliopatria) 仓库中的 `cliopatria.geojson.zip`，解压后改名（开发时用的是 v0.21） |
| `china-chronology-data.js` | npm 包 `china-chronology@0.1.0` 中的 `dist/data-*.js` |
| `natural-earth/ne_50m_land.geojson`、`ne_50m_lakes.geojson`、`ne_50m_rivers_lake_centerlines.geojson` | [Natural Earth](https://github.com/nvkelso/natural-earth-vector/tree/master/geojson) |
| `three-globe-img/earth-blue-marble.jpg`、`earth-topology.png` | npm 包 `three-globe` 的 `example/img/`（NASA Blue Marble 影像） |

## 运行顺序（在 `tools/` 目录下）

```bash
mkdir -p out
python3 prepare.py                     # 筛选前800年以后的政权，生成中文名表与年号表
python3 geo3.py 0.02 0.045 0.04 out    # 简化疆域形状并编码为 geoms.bin
python3 build.py                       # 合并译名、配色、纪年、事件、城市 → out/data.json
python3 basemap.py                     # 生成底图 out/base.jpg 与陆地遮罩 out/land.png
python3 make_web_assets.py             # 写入 ../assets/*.js
```

## 各文件的作用

- `zh_asia.tsv`、`zh_west.tsv`：1521 个政权的中文译名（英文名 → 中文名）。
- `content_text.py`：“同一时刻”大事、“此时世界”解说、朝代与世界分期色带、城市古称、政权注记。
- `build.py`：按年代区分同名政权（如 Later Zhou 的东周与后周）、配色、纪年（周王、鲁公、秦王、汉初帝王纪年与年号）。
- `geo3.py`：参数依次为相邻时段复用阈值、简化容差（度）、坐标量化步长（度）。
