# Lion City Rent Atlas

面向公众的新加坡租金可视化项目，按区域、按房型看 `Condo` 与 `HDB` 的租金分布。

[English README](README.en.md)

在线访问：
- https://sasyatitech.github.io/nus_lease/

项目仓库：
- https://github.com/SasyaTitech/nus_lease

如果这个项目对你有帮助，欢迎赏一颗 Star：
- https://github.com/SasyaTitech/nus_lease

作者：
- Sasya / https://github.com/SasyaTitech

## 这个网页能看什么

当前网页分成两个视图：

- `Condo`
  - 看私宅租金在不同 district 的分布
  - 看不同房型的热力图
  - 看各 district 的排序和覆盖情况
  - 如果挂牌数据可用，还能看挂牌价和成交价的对比
- `HDB`
  - 看各 town 的 HDB 租金分布
  - 看不同 flat type 的热力图
  - 看各 town 的官方租金排序

最简单的使用方式就是：

1. 打开网页。
2. 在 `Condo` 和 `HDB` 之间切换。
3. 再按房型或房间数缩小范围。

## 数据公开说明

### Condo 成交数据

Condo 成交数据来自 `URA` 的私宅租约数据。

官方参考：
- URA 租约查询页：https://eservice.ura.gov.sg/property-market-information/pmiResidentialRentalSearch
- URA API 门户：https://eservice.ura.gov.sg/maps/api/

这层数据的含义是：
- 它是官方私宅租约来源。
- 它覆盖提交给 `IRAS` 做印花税评估的私宅租赁合同。
- 它不包含 `HDB`。
- `non-landed` 记录通常带有 bedroom 信息，但仍有部分记录缺失。
- `URA` 不提供 bathroom count。

### HDB 数据

HDB 数据来自官方开放数据集。

官方来源：
- https://data.gov.sg/datasets/d_c9f57187485a850908655db0e8cfe651/view

这层数据的含义是：
- 它是官方 HDB 租赁相关数据。
- 网页里会把最近窗口内的数据聚合成 `town x flat type`。

### 地图边界说明

网页上的 `D01-D28` 地图不是官方精确 postal district polygon。

它是基于公开的 `URA planning area` 边界，进一步合并出来的 district proxy layer，所以更适合做市场阅读和区域比较，而不是法律或测绘用途。

官方边界来源：
- https://data.gov.sg/datasets/d_2cc750190544007400b2cfd5d7f53209/view

### 挂牌价说明

代码仓库里保留了 `PropertyGuru` 挂牌价适配层，但公开网页不一定始终启用这一层。

原因很简单：
- 挂牌价不是成交价
- 挂牌页面可能会遇到反爬或挑战页
- 挂牌覆盖稳定性天然不如官方成交口径

## 仓库里公开了什么

公开仓库只保留网页渲染所需要的内容：

- `web/`
- `data/processed/market_snapshot.json`
- `data/fixtures/demo_market_snapshot.json`
- `data/raw/planning_area_boundaries.geojson`
- `data/raw/district_centroids.json`

像下面这些本地原始导出不会默认进入仓库：

- URA 原始拉取结果
- HDB 原始拉取结果
- PropertyGuru 浏览器导出的 HTML
- 本地缓存和构建垃圾

具体规则见：
- [.gitignore](.gitignore)

## 本地运行

```bash
python3 -m pip install -e .
python3 -m http.server 8000
```

然后打开：

- http://localhost:8000/web/

## 如果你想自己生成新数据

### 1. 拉公开边界辅助数据

```bash
python3 scripts/fetch_planning_area_boundaries.py
python3 scripts/fetch_district_centroids.py
python3 scripts/fetch_subzone_boundaries.py
```

### 2. 拉 URA 的 Condo 成交数据

先导出你自己的 `URA_ACCESS_KEY`：

```bash
export URA_ACCESS_KEY='your-access-key'
```

然后抓最近窗口的私宅租约：

```bash
python3 scripts/fetch_ura_private_rentals.py --months 6
```

输出：

- `data/raw/ura_private_rentals.json`

### 3. 拉 HDB 数据

```bash
python3 scripts/fetch_hdb_rentals.py --months 3
```

输出：

- `data/raw/hdb_rentals.json`

### 4. 生成网页快照

```bash
python3 scripts/build_market_snapshot.py --hdb data/raw/hdb_rentals.json
python3 scripts/build_district_boundaries.py
```

输出：

- `data/processed/market_snapshot.json`
- `data/processed/district_boundaries.geojson`
- `data/processed/district_label_points.json`

## 可选：挂牌价采集

如果你想扩展成带挂牌价的版本，可以继续走挂牌抓取管线。

### 解析浏览器导出的挂牌 HTML

```bash
python3 scripts/import_propertyguru_html.py
```

预期输入目录：

- `data/raw/propertyguru_html/`

预期输出：

- `data/raw/propertyguru_listings.json`

### 尝试用 Playwright 直接抓取

```bash
python3 -m playwright install chromium
python3 scripts/fetch_propertyguru_live.py \
  --url 'https://www.propertyguru.com.sg/apartment-condo-for-rent/in-singapore'
```

如果站点返回 challenge page，这条路可能会失败。

## 部署

仓库里已经带了 `GitHub Pages` 工作流：

- [.github/workflows/deploy-pages.yml](.github/workflows/deploy-pages.yml)

如果你 fork 这个项目，只需要把 Pages 的发布源设成 `GitHub Actions`，然后推到 `main` 即可。

## 贡献

欢迎提交：

- 数据源建议
- 地图边界修正
- UI/交互改进
- issue 和 PR

如果这个项目对你有帮助，欢迎赏一颗 Star：
- https://github.com/SasyaTitech/nus_lease
