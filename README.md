# nus_lease

全新加坡租赁展示程序，当前分成两个模式：

- `Condo`
  - `挂牌价`: PropertyGuru 公开搜索结果页里的当前 asking rent
  - `成交价`: URA 官方 `Private Residential Properties Rental Contract` API
- `HDB`
  - 单一官方口径：HDB `Renting Out of Flats` 明细，按最近几个月聚合成 `town x flat type`

当前版本重点是把 `Condo 的挂牌 vs 成交` 跑通，同时让 `HDB` 走一套更干净的单口径界面。

## 为什么成交数据要用 URA

`URA` 的 [Private Residential Rental Contracts](https://eservice.ura.gov.sg/property-market-information/pmiResidentialRentalSearch) 明确写的是：

- 私宅租赁合同，来自“submitted to `IRAS` for Stamp Duty assessment”
- 覆盖 `last 60 months`
- 每月 `15th` 更新，若遇周末/公假则顺延工作日

`URA API` 文档同样说明：

- `PMI_Resi_Rental` 返回过去 `5` 年的私宅租赁合同
- 超过 `5` 年的记录可能被修改或作废，建议只保留最近 `5` 年
- 字段里有 `district / propertyType / rent / noOfBedRoom / leaseDate / x / y`

这意味着它是目前做“官方成交租金”最稳的一手源。它很全面，但不是“宇宙真全集”：

- 对于**正式签约并提交印花税评估**的私宅租约，覆盖面很高
- 它**不包含 HDB**
- `noOfBedRoom` 只对 `non-landed` 可用，而且有些记录为空
- **没有 bathroom count**，所以 `2BR2BA` 只能在挂牌侧做
- API 需要你先注册 URA 账号，拿 `AccessKey`

## 为什么挂牌数据单独走 PropertyGuru

PropertyGuru 更像“实时市场温度计”：

- 能看到当前 asking rent
- 能按 `Studio / 2BR / 3BR` 甚至 `2BR2BA` 这类挂牌结构来切
- 但它不是成交数据库

问题也很直接：

- 公开页面有 `Cloudflare` challenge
- 普通脚本请求会被 `403`
- 自动抓取稳定性和条款风险都高于官方 API

所以这个仓库把 PropertyGuru 设计成 **adapter**：

- 优先解析你从真实浏览器导出的 HTML
- 也保留了 Playwright 拉取入口
- 一旦被 challenge 卡住，整套 dashboard 仍然能靠 URA 官方成交层运行

## 当前可视化设计

前端用的是：

- `Apache ECharts`: 热图、散点图、排行条形图
- `GSAP`: 进场动画

我没有直接做连续地理热力图，原因很简单：

- 官方成交数据天然是 `district + project` 粒度
- 直接做一片模糊发光的连续热力，会让区域边界和样本密度失真

现在的首版展示：

- `Condo`
  - `District Map`: 官方 `planning area` 底图 + `D01-D28` district 编号层
  - `District Heatmap`: `district x 房型`
  - `Price Gap Scatter`: 横轴成交，纵轴挂牌
  - `Price Gap Ranking`: 各 district 的挂牌-成交价差
- `HDB`
  - `Town Treemap`: 面积看样本量，颜色看中位租金
  - `HDB Heatmap`: `town x flat type`
  - `Town Ranking`: 各 town 官方中位租金排序

## 安装

```bash
python3 -m pip install -e .
python3 -m playwright install chromium
```

## 生成演示数据

```bash
python3 scripts/fetch_planning_area_boundaries.py
python3 scripts/fetch_district_centroids.py
python3 scripts/build_demo_fixture.py
```

默认只会写：

- `data/fixtures/demo_market_snapshot.json`

如果你明确想让 demo 覆盖 `processed snapshot`，再加：

```bash
python3 scripts/build_demo_fixture.py --sync-processed
```

## 拉官方成交数据

先去 URA 注册账号并拿到 `AccessKey`，然后：

```bash
export URA_ACCESS_KEY='your-access-key'
python3 scripts/fetch_ura_private_rentals.py --months 3
```

这会写出：

- `data/raw/ura_private_rentals.json`

## 导入挂牌数据

### 方案 A：推荐

用真实浏览器打开 PropertyGuru 搜索页，保存 HTML 到 `data/raw/propertyguru_html/`，再运行：

```bash
python3 scripts/import_propertyguru_html.py
```

### 方案 B：尝试自动抓取

```bash
python3 scripts/fetch_propertyguru_live.py \
  --url 'https://www.propertyguru.com.sg/apartment-condo-for-rent/in-singapore'
```

如果出现 `Cloudflare challenge`，脚本会直接退出并提示你改用浏览器导出 HTML。

## 拉 HDB 官方数据

```bash
python3 scripts/fetch_hdb_rentals.py --months 3
```

这会写出：

- `data/raw/hdb_rentals.json`

## 生成 dashboard 数据

```bash
python3 scripts/build_market_snapshot.py --hdb data/raw/hdb_rentals.json
```

产物：

- `data/processed/market_snapshot.json`
- `data/raw/planning_area_boundaries.geojson`
- `data/raw/district_centroids.json`
- `data/raw/hdb_rentals.json`

## 启动页面

在仓库根目录执行：

```bash
python3 -m http.server 8000
```

然后打开：

- `http://localhost:8000/web/`

## 发布给别人用

最省事的是直接用 `GitHub Pages`，因为这个项目当前就是纯静态页面，不需要后端。

仓库里已经带了：

- `/.github/workflows/deploy-pages.yml`
- `/index.html`

它会自动把下面这些文件发布出去：

- `web/`
- `data/processed/market_snapshot.json`
- `data/fixtures/demo_market_snapshot.json`
- `data/raw/planning_area_boundaries.geojson`
- `data/raw/district_centroids.json`

不会把整份 `raw` 数据目录一起暴露出去。

仓库根目录也已经加了 [`.gitignore`](/data1/sasya/project/nus_lease/.gitignore)：

- 默认忽略 `data/raw/` 里的租约和挂牌原始导出
- 只保留会被页面直接依赖的公开边界文件
- 忽略本地缓存、`__pycache__` 和 `egg-info`

### 你要做的事

1. 把这个目录推到你的 GitHub 仓库。
2. 默认分支用 `main`。
3. 打开 GitHub 仓库的 `Settings -> Pages`。
4. 在 `Build and deployment` 里把 `Source` 选成 `GitHub Actions`。
5. 推一次代码，等 `Deploy GitHub Pages` workflow 跑完。

部署后，默认访问地址通常会是：

- `https://<你的用户名>.github.io/<仓库名>/`

根路径会自动跳到：

- `/web/`

### 发布前注意

- `GitHub Pages` 是公开站点，页面里用到的 JSON 任何人都能看到。
- 不要把 `URA_ACCESS_KEY`、原始凭证文件或你不想公开的原始数据提交到仓库。
- 如果你不想公开整仓库，先确认你的 GitHub 计划是否支持私有仓库配 `GitHub Pages`。

## 下一步建议

- 给 `HDB` 加 town 详情抽屉，点进某个 town 看不同 flat type 的分布
- 给 PropertyGuru adapter 增加“项目页采集”，补更细的 condo 户型标签
- 引入时间维度，做近 `3 / 6 / 12` 个月的 condo 挂牌-成交偏离变化
