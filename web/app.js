const SNAPSHOT_SOURCES = [
  "../data/processed/market_snapshot.json",
  "../data/fixtures/demo_market_snapshot.json",
];

const DISTRICT_BOUNDARY_SOURCES = [
  "../data/processed/district_boundaries.geojson",
];

const DISTRICT_LABEL_POINT_SOURCES = [
  "../data/processed/district_label_points.json",
];

const PLANNING_AREA_SOURCES = [
  "../data/raw/planning_area_boundaries.geojson",
];

const DISTRICT_POINT_SOURCES = [
  "../data/raw/district_centroids.json",
];

const MIN_CONDO_TRANSACTION_COUNT = 20;

const CONDO_COPY = {
  hero:
    "Condo 视图把区域分布、房型结构和租金层级放到同一页里。需要的时候，还可以继续比较挂牌价和官方成交价之间的偏离。",
  contextTitle: "District Choropleth",
  contextSubtitle:
    "地图只显示已被成交证据或人工校正确认过的区块；查不清的 subzone 会直接留空，不再强行拼接。",
  heatmapTitle: "Condo Heatmap",
  heatmapSubtitle:
    "按 `district x bedroom bucket` 展示当前筛选下的主指标，hover 里看挂牌、成交和溢价。",
  scatterTitle: "Price Gap Scatter",
  scatterSubtitle: "横轴成交中位数，纵轴挂牌中位数，泡泡大小代表挂牌量。",
  rankingTitle: "Price Gap Ranking",
  rankingSubtitle: "同一房型里，全部 district 的挂牌和成交价差排序。",
};

const CONDO_TX_ONLY_COPY = {
  hero:
    "Condo 视图当前聚焦官方成交租金。按房型切换后，可以直接比较不同 district 的租金层级和样本覆盖。",
  contextTitle: "District Choropleth",
  contextSubtitle:
    "地图只显示已被成交证据或人工校正确认过的区块；低于 20 笔成交的 bucket 不参与聚合，查不清的 subzone 会留空。",
  heatmapTitle: "Condo Heatmap",
  heatmapSubtitle:
    "按 `district x bedroom bucket` 展示当前筛选下的官方成交中位数与样本量；低于 20 笔成交的格子自动留空。",
  rankingTitle: "Transaction Ranking",
  rankingSubtitle: "按当前房型对各 district 的官方成交中位数排序，仅保留样本量达到 20 的格子或聚合区。",
};

const HDB_COPY = {
  hero:
    "HDB 视图聚焦最近窗口内的官方租金数据，更适合直接看各 town、各房型的租金层级与样本量。",
  contextTitle: "Town Treemap",
  contextSubtitle: "每个 town 的面积代表样本量，颜色代表最近窗口内的中位租金。",
  heatmapTitle: "HDB Heatmap",
  heatmapSubtitle: "按 `town x flat type` 展示最近窗口内的中位租金，hover 里看样本量。",
  rankingTitle: "Town Ranking",
  rankingSubtitle: "当前 flat type 下，各 town 的官方租金中位数排序。",
};

const metricLabels = {
  premium_pct: "挂牌溢价",
  delta: "挂牌 - 成交",
  listing_median: "挂牌中位数",
  transaction_median: "成交中位数",
  median_rent: "中位租金",
};

const palettes = {
  premium_pct: ["#23475b", "#178d9a", "#72d9d3", "#ffe29b", "#ff9a4c", "#ff6b3d"],
  delta: ["#244a5d", "#1f9aa0", "#82ebe0", "#ffd99b", "#ff9347"],
  listing_median: ["#244a5d", "#1f9aa0", "#82ebe0", "#ffd99b", "#ff9347"],
  transaction_median: ["#244a5d", "#1f9aa0", "#82ebe0", "#ffd99b", "#ff9347"],
  median_rent: ["#244a5d", "#1f9aa0", "#82ebe0", "#ffd99b", "#ff9347"],
};

const planningAreaDistrictMap = {
  "ANG MO KIO": "20",
  "BEDOK": "16",
  "BISHAN": "20",
  "BOON LAY": "22",
  "BUKIT BATOK": "23",
  "BUKIT MERAH": "04",
  "BUKIT PANJANG": "23",
  "BUKIT TIMAH": "21",
  "CENTRAL WATER CATCHMENT": "26",
  "CHANGI": "17",
  "CHANGI BAY": "17",
  "CHOA CHU KANG": "23",
  "CLEMENTI": "05",
  "DOWNTOWN CORE": "01",
  "GEYLANG": "14",
  "HOUGANG": "19",
  "JURONG EAST": "22",
  "JURONG WEST": "22",
  "KALLANG": "08",
  "LIM CHU KANG": "24",
  "MANDAI": "25",
  "MARINA EAST": "01",
  "MARINA SOUTH": "01",
  "MARINE PARADE": "15",
  "MUSEUM": "06",
  "NEWTON": "11",
  "NORTH-EASTERN ISLANDS": "19",
  "NOVENA": "11",
  "ORCHARD": "09",
  "OUTRAM": "02",
  "PASIR RIS": "18",
  "PAYA LEBAR": "14",
  "PIONEER": "22",
  "PUNGGOL": "19",
  "QUEENSTOWN": "03",
  "RIVER VALLEY": "09",
  "ROCHOR": "07",
  "SELETAR": "28",
  "SEMBAWANG": "27",
  "SENGKANG": "19",
  "SERANGOON": "13",
  "SIMPANG": "28",
  "SINGAPORE RIVER": "06",
  "SOUTHERN ISLANDS": "04",
  "STRAITS VIEW": "01",
  "SUNGEI KADUT": "25",
  "TAMPINES": "18",
  "TANGLIN": "10",
  "TENGAH": "24",
  "TOA PAYOH": "12",
  "TUAS": "22",
  "WESTERN ISLANDS": "22",
  "WESTERN WATER CATCHMENT": "24",
  "WOODLANDS": "25",
  "YISHUN": "27",
};

const districtLabelOverrides = {
  "01": [103.8548, 1.2848],
  "02": [103.8447, 1.2777],
  "03": [103.8008, 1.2925],
  "04": [103.8238, 1.2662],
  "05": [103.7704, 1.3074],
  "06": [103.8462, 1.2886],
  "07": [103.8573, 1.3006],
  "08": [103.8536, 1.3112],
  "09": [103.8378, 1.2977],
  "10": [103.8154, 1.3185],
  "11": [103.8409, 1.3226],
  "12": [103.8543, 1.3301],
  "13": [103.8708, 1.3318],
  "14": [103.8911, 1.3185],
  "15": [103.9047, 1.3024],
  "16": [103.9343, 1.3186],
  "17": [103.9894, 1.3915],
  "18": [103.9452, 1.3532],
  "19": [103.8941, 1.3908],
  "20": [103.8487, 1.3504],
  "21": [103.7756, 1.3399],
  "22": [103.7429, 1.3338],
  "23": [103.7612, 1.3787],
  "24": [103.7303, 1.3595],
  "25": [103.7622, 1.4248],
  "26": [103.8213, 1.3968],
  "27": [103.8358, 1.4299],
  "28": [103.8768, 1.4082],
};

const currency = new Intl.NumberFormat("en-SG", {
  style: "currency",
  currency: "SGD",
  maximumFractionDigits: 0,
});

const percent = new Intl.NumberFormat("en-US", {
  style: "percent",
  maximumFractionDigits: 1,
});

function isFiniteNumber(value) {
  return typeof value === "number" && Number.isFinite(value);
}

function formatCompactCurrency(value) {
  if (!isFiniteNumber(value)) return "N/A";
  if (value >= 10000) return `$${Math.round(value / 1000)}k`;
  return `$${(value / 1000).toFixed(1)}k`;
}

function formatMetric(metric, value) {
  if (!isFiniteNumber(value)) return "No data";
  if (metric === "premium_pct") return percent.format(value);
  return currency.format(value);
}

function paletteForMetric(metric) {
  return palettes[metric] || palettes.transaction_median;
}

function metricDomain(metric, rows) {
  const values = rows
    .map((row) => row?.[metric])
    .filter(isFiniteNumber);
  if (!values.length) return { min: 0, max: 1 };
  let min = Math.min(...values);
  let max = Math.max(...values);
  if (min === max) {
    min -= 1;
    max += 1;
  }
  return { min, max };
}

function extractPolygons(geometry) {
  if (!geometry) return [];
  if (geometry.type === "Polygon") return [geometry.coordinates];
  if (geometry.type === "MultiPolygon") return geometry.coordinates || [];
  return [];
}

function buildDistrictGeoJSON(planningAreaGeoJSON) {
  if (!planningAreaGeoJSON?.features?.length) return null;

  const grouped = new Map();
  for (const feature of planningAreaGeoJSON.features) {
    const planningArea = feature.properties?.PLN_AREA_N;
    const district = planningAreaDistrictMap[planningArea];
    if (!district) continue;
    if (!grouped.has(district)) grouped.set(district, []);
    grouped.get(district).push(...extractPolygons(feature.geometry));
  }

  return {
    type: "FeatureCollection",
    features: [...grouped.entries()].map(([district, polygons]) => ({
      type: "Feature",
      properties: {
        name: district,
        district,
        district_name: districtRowsName(district),
      },
      geometry: {
        type: "MultiPolygon",
        coordinates: polygons,
      },
    })),
  };
}

function districtRowsName(district) {
  const rows = {
    "01": "Boat Quay / Raffles Place / Marina",
    "02": "Chinatown / Tanjong Pagar",
    "03": "Alexandra / Commonwealth",
    "04": "Harbourfront / Telok Blangah",
    "05": "Buona Vista / West Coast / Clementi New Town",
    "06": "City Hall / Clarke Quay",
    "07": "Beach Road / Bugis / Rochor",
    "08": "Farrer Park / Serangoon Rd",
    "09": "Orchard / River Valley",
    "10": "Ardmore / Bukit Timah / Holland Rd / Tanglin",
    "11": "Watten Estate / Novena / Thomson",
    "12": "Balestier / Toa Payoh / Serangoon",
    "13": "Macpherson / Potong Pasir",
    "14": "Eunos / Geylang / Paya Lebar",
    "15": "East Coast / Marine Parade",
    "16": "Bedok / Upper East Coast",
    "17": "Changi Airport / Changi Village",
    "18": "Pasir Ris / Tampines",
    "19": "Hougang / Punggol / Sengkang",
    "20": "Ang Mo Kio / Bishan / Thomson",
    "21": "Clementi Park / Upper Bukit Timah",
    "22": "Boon Lay / Jurong / Tuas",
    "23": "Dairy Farm / Bukit Panjang / Choa Chu Kang",
    "24": "Lim Chu Kang / Tengah",
    "25": "Kranji / Woodgrove",
    "26": "Upper Thomson / Springleaf",
    "27": "Yishun / Sembawang",
    "28": "Seletar / Yio Chu Kang",
  };
  return rows[district] || district;
}

function steppedColor(value, metric, domain) {
  if (!isFiniteNumber(value)) return "rgba(64, 82, 94, 0.55)";
  const palette = paletteForMetric(metric);
  const ratio = Math.max(0, Math.min(1, (value - domain.min) / (domain.max - domain.min)));
  const index = Math.min(palette.length - 1, Math.floor(ratio * palette.length));
  return palette[index];
}

async function loadFirstAvailable(paths) {
  for (const path of paths) {
    try {
      const response = await fetch(path);
      if (!response.ok) continue;
      const data = await response.json();
      data._sourcePath = path;
      return data;
    } catch (_error) {
      // Ignore and fall back.
    }
  }
  throw new Error(`No available source from: ${paths.join(", ")}`);
}

async function loadOptional(paths) {
  try {
    return await loadFirstAvailable(paths);
  } catch (_error) {
    return null;
  }
}

function median(values) {
  const ordered = [...values].sort((a, b) => a - b);
  if (!ordered.length) return null;
  const mid = Math.floor(ordered.length / 2);
  return ordered.length % 2 ? ordered[mid] : (ordered[mid - 1] + ordered[mid]) / 2;
}

function simpleAverage(values) {
  const valid = values.filter(isFiniteNumber);
  if (!valid.length) return null;
  return valid.reduce((sum, value) => sum + value, 0) / valid.length;
}

function hasCondoListingData(snapshot) {
  const rows = snapshot.condo?.districts || [];
  return rows.some((row) => isFiniteNumber(row.listing_median) || (row.listing_count || 0) > 0);
}

function condoWindowLabel(snapshotMeta) {
  const txMeta = snapshotMeta?.transactions_meta;
  if (!txMeta?.window_start || !txMeta?.window_end) return "official rental contracts";
  return `${txMeta.window_start.slice(0, 7)} to ${txMeta.window_end.slice(0, 7)}`;
}

function isReliableCondoTransactionRow(row, listingAvailable) {
  if (listingAvailable) return true;
  return isFiniteNumber(row.transaction_median) && (row.transaction_count || 0) >= MIN_CONDO_TRANSACTION_COUNT;
}

function filterReliableCondoRows(rows, listingAvailable) {
  return listingAvailable ? rows : rows.filter((row) => isReliableCondoTransactionRow(row, listingAvailable));
}

function condoTooltipLines(row, listingAvailable, bucket = null, suppressed = false) {
  const lines = [
    `<strong>D${row.district} ${row.district_name}</strong>`,
  ];
  if (bucket) lines.push(bucket);
  lines.push(`成交: ${formatMetric("transaction_median", row.transaction_median)}`);
  if (listingAvailable) {
    lines.push(`挂牌: ${formatMetric("listing_median", row.listing_median)}`);
    lines.push(`价差: ${formatMetric("delta", row.delta)}`);
    lines.push(`溢价: ${formatMetric("premium_pct", row.premium_pct)}`);
    if (row.listing_count !== undefined) lines.push(`挂牌样本: ${row.listing_count}`);
  }
  if (row.transaction_count !== undefined) lines.push(`成交样本: ${row.transaction_count}`);
  if (suppressed) {
    lines.push(`低样本隐藏: 少于 ${MIN_CONDO_TRANSACTION_COUNT} 笔官方成交`);
  }
  return lines;
}

function getCondoRows(snapshot, bucket) {
  const rows = (snapshot.condo?.districts || []).filter((row) => row.segment === "non-landed" || !row.segment);
  return rows.filter((row) => bucket === "all" || row.bedroom_bucket === bucket);
}

function getCondoDistrictComparison(rows, bucket, listingAvailable) {
  if (bucket !== "all") {
    return filterReliableCondoRows(
      rows.filter((row) => isFiniteNumber(row.listing_median) || isFiniteNumber(row.transaction_median)),
      listingAvailable,
    );
  }

  const grouped = new Map();
  for (const row of rows) {
    if (!grouped.has(row.district)) grouped.set(row.district, []);
    grouped.get(row.district).push(row);
  }

  return [...grouped.entries()]
    .map(([district, group]) => {
      const visibleGroup = filterReliableCondoRows(group, listingAvailable);
      if (!visibleGroup.length) return null;
      const listingMedian = simpleAverage(visibleGroup.map((row) => row.listing_median));
      const transactionMedian = simpleAverage(visibleGroup.map((row) => row.transaction_median));
      const delta = isFiniteNumber(listingMedian) && isFiniteNumber(transactionMedian)
        ? listingMedian - transactionMedian
        : null;
      return {
        district,
        district_name: group[0].district_name,
        bedroom_bucket: "All Buckets",
        listing_median: listingMedian,
        transaction_median: transactionMedian,
        delta,
        premium_pct: isFiniteNumber(delta) && isFiniteNumber(transactionMedian)
          ? delta / transactionMedian
          : null,
        listing_count: visibleGroup.reduce((sum, row) => sum + (row.listing_count || 0), 0),
        transaction_count: visibleGroup.reduce((sum, row) => sum + (row.transaction_count || 0), 0),
        transaction_project_count: visibleGroup.reduce((sum, row) => sum + (row.transaction_project_count || 0), 0),
        listing_layout_medians: {},
      };
    })
    .filter(Boolean);
}

function getHdbRows(snapshot, flatType) {
  const rows = snapshot.hdb?.towns || [];
  return rows.filter((row) => flatType === "all" || row.flat_type === flatType);
}

function getHdbTownComparison(rows, flatType) {
  if (flatType !== "all") {
    return rows.filter((row) => isFiniteNumber(row.median_rent));
  }

  const grouped = new Map();
  for (const row of rows) {
    if (!grouped.has(row.town)) grouped.set(row.town, []);
    grouped.get(row.town).push(row);
  }

  return [...grouped.entries()].map(([town, group]) => ({
    town,
    flat_type: "All Flat Types",
    median_rent: simpleAverage(group.map((row) => row.median_rent)),
    approval_count: group.reduce((sum, row) => sum + (row.approval_count || 0), 0),
  }));
}

function condoMetrics(rows, listingAvailable, snapshotMeta, totalDistrictCount) {
  const premiums = rows
    .map((row) => row.premium_pct)
    .filter(isFiniteNumber);
  const listingMedians = rows
    .map((row) => row.listing_median)
    .filter(isFiniteNumber);
  const transactionMedians = rows
    .map((row) => row.transaction_median)
    .filter(isFiniteNumber);
  const listingCount = rows.reduce((sum, row) => sum + (row.listing_count || 0), 0);
  const transactionCount = rows.reduce((sum, row) => sum + (row.transaction_count || 0), 0);
  const activeDistricts = new Set(
    rows
      .filter((row) => isFiniteNumber(row.listing_median) || isFiniteNumber(row.transaction_median))
      .map((row) => row.district),
  ).size;
  return [
    {
      label: listingAvailable ? "Median Listing Premium" : "Transaction Window",
      value: listingAvailable ? (premiums.length ? percent.format(median(premiums)) : "N/A") : condoWindowLabel(snapshotMeta),
      sub: listingAvailable ? `${listingCount} listing observations` : `${transactionCount} official rental contracts`,
    },
    {
      label: listingAvailable ? "Median Asking Rent" : "Median Transaction Rent",
      value: listingAvailable
        ? (listingMedians.length ? currency.format(median(listingMedians)) : "N/A")
        : (transactionMedians.length ? currency.format(median(transactionMedians)) : "N/A"),
      sub: listingAvailable ? "Current condo asking rents" : "Official condo rental contracts",
    },
    {
      label: "Median Transaction Rent",
      value: transactionMedians.length ? currency.format(median(transactionMedians)) : "N/A",
      sub: `${transactionCount} official rental contracts`,
    },
    {
      label: "District Coverage",
      value: `${activeDistricts} / ${totalDistrictCount}`,
      sub: listingAvailable ? "districts with listing or transaction data" : `districts above ${MIN_CONDO_TRANSACTION_COUNT} contract floor`,
    },
  ];
}

function hdbMetrics(townRows, snapshotMeta, totalTownCount) {
  const rents = townRows
    .map((row) => row.median_rent)
    .filter(isFiniteNumber);
  const approvals = townRows.reduce((sum, row) => sum + (row.approval_count || 0), 0);
  const activeTowns = new Set(
    townRows
      .filter((row) => isFiniteNumber(row.median_rent))
      .map((row) => row.town),
  ).size;
  const latestMonth = snapshotMeta?.hdb_meta?.latest_available_month;
  const windowStart = snapshotMeta?.hdb_meta?.window_start;
  return [
    {
      label: "Median Approved Rent",
      value: rents.length ? currency.format(median(rents)) : "N/A",
      sub: "Official HDB rental approvals",
    },
    {
      label: "Approval Observations",
      value: approvals.toLocaleString("en-US"),
      sub: "latest rolling window",
    },
    {
      label: "Town Coverage",
      value: `${activeTowns} / ${totalTownCount}`,
      sub: "towns with available approvals",
    },
    {
      label: "Data Window",
      value: latestMonth ? latestMonth.slice(0, 7) : "Demo",
      sub: windowStart ? `from ${windowStart.slice(0, 7)}` : "single official source",
    },
  ];
}

function renderMetrics(cards) {
  const container = document.getElementById("hero-metrics");
  container.innerHTML = cards
    .map(
      (item) => `
        <div class="metric-card">
          <div class="label">${item.label}</div>
          <div class="value">${item.value}</div>
          <div class="sub">${item.sub}</div>
        </div>
      `,
    )
    .join("");
}

function renderStatus(snapshot) {
  const status = document.getElementById("dataset-status");
  const isDemo = snapshot.meta?.mode === "demo" || snapshot._sourcePath.includes("demo");
  const sourceName = isDemo ? "演示快照" : "公开实时快照";
  const generatedAt = snapshot.meta?.generated_at || "unknown";
  status.classList.toggle("is-demo", isDemo);
  status.innerHTML = `
    <span class="status-badge ${isDemo ? "is-demo" : "is-live"}">${isDemo ? "DEMO" : "LIVE"}</span>
    <strong>${sourceName}</strong><br />
    更新于 ${generatedAt}
  `;

  const listingAvailable = hasCondoListingData(snapshot);
  const notes = [
    "Condo 成交数据来自 URA 私宅租约申报；HDB 数据来自官方 rental approvals。",
    listingAvailable
      ? "挂牌价代表当前在线 asking rent，不等于已成交租金。"
      : "当前公开站点先展示官方成交与官方 HDB 口径，挂牌侧会在后续补入。",
    "Condo 地图只保留成交证据足够强或人工校正过的 subzone；不再使用最近邻或 planning-area fallback 去硬补邮区。",
    `为减少噪声，Condo 成交少于 ${MIN_CONDO_TRANSACTION_COUNT} 笔的格子会被隐藏。`,
  ];
  document.getElementById("notes-list").innerHTML = notes.map((note) => `<li>${note}</li>`).join("");
}

function renderMarketTabs(market) {
  document.querySelectorAll(".market-tab").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.market === market);
  });
}

function renderModeCopy(market, listingAvailable) {
  const copy = market === "condo" ? (listingAvailable ? CONDO_COPY : CONDO_TX_ONLY_COPY) : HDB_COPY;
  document.getElementById("hero-text").textContent = copy.hero;
  document.getElementById("context-title").textContent = copy.contextTitle;
  document.getElementById("context-subtitle").textContent = copy.contextSubtitle;
  document.getElementById("heatmap-title").textContent = copy.heatmapTitle;
  document.getElementById("heatmap-subtitle").textContent = copy.heatmapSubtitle;
  document.getElementById("ranking-title").textContent = copy.rankingTitle;
  document.getElementById("ranking-subtitle").textContent = copy.rankingSubtitle;
  document.getElementById("scatter-title").textContent = CONDO_COPY.scatterTitle;
  document.getElementById("scatter-subtitle").textContent = CONDO_COPY.scatterSubtitle;
}

function renderControls(market, listingAvailable) {
  document.getElementById("condo-bucket-control").classList.toggle("hidden", market !== "condo");
  document.getElementById("metric-control").classList.toggle("hidden", market !== "condo" || !listingAvailable);
  document.getElementById("hdb-flat-control").classList.toggle("hidden", market !== "hdb");
  document.getElementById("scatter-panel").classList.toggle("hidden", market !== "condo" || !listingAvailable);
}

function setChartHeights(market, primaryRows, comparisonRows) {
  if (market === "condo") {
    document.getElementById("context-chart").style.height = "680px";
    document.getElementById("heatmap").style.height = `${Math.max(680, new Set(primaryRows.map((row) => row.district)).size * 28 + 180)}px`;
    document.getElementById("ranking").style.height = `${Math.max(640, comparisonRows.length * 24 + 120)}px`;
    return;
  }
  document.getElementById("context-chart").style.height = "620px";
  document.getElementById("heatmap").style.height = `${Math.max(720, new Set(primaryRows.map((row) => row.town)).size * 22 + 170)}px`;
  document.getElementById("ranking").style.height = `${Math.max(700, comparisonRows.length * 24 + 120)}px`;
}

function visualMapFormatter(metric) {
  return (value) => (metric === "premium_pct" ? percent.format(value) : formatCompactCurrency(value));
}

function buildCondoHeatmapOption(rows, metric, listingAvailable) {
  const buckets = [...new Set(rows.map((row) => row.bedroom_bucket))];
  const districts = [...new Set(rows.map((row) => row.district))];
  const domain = metricDomain(
    metric,
    rows.filter((row) => isReliableCondoTransactionRow(row, listingAvailable)),
  );
  const values = rows.map((row) => ({
    value: [
      buckets.indexOf(row.bedroom_bucket),
      districts.indexOf(row.district),
      isReliableCondoTransactionRow(row, listingAvailable) ? row[metric] : null,
    ],
    row: {
      ...row,
      suppressed: !isReliableCondoTransactionRow(row, listingAvailable),
    },
  }));

  return {
    backgroundColor: "transparent",
    animationDuration: 700,
    grid: { top: 18, right: 12, bottom: 70, left: 110 },
    tooltip: {
      confine: true,
      backgroundColor: "rgba(7, 20, 27, 0.95)",
      borderColor: "rgba(255,255,255,0.08)",
      textStyle: { color: "#edf6f5" },
      formatter: (params) => {
        const row = params.data.row;
        return condoTooltipLines(row, listingAvailable, row.bedroom_bucket, row.suppressed).join("<br />");
      },
    },
    xAxis: {
      type: "category",
      data: buckets,
      axisLabel: { color: "#c7d8d7" },
      axisLine: { lineStyle: { color: "rgba(255,255,255,0.12)" } },
    },
    yAxis: {
      type: "category",
      inverse: true,
      data: districts.map((district) => `D${district}`),
      axisLabel: { color: "#c7d8d7", interval: 0, margin: 14 },
      axisLine: { lineStyle: { color: "rgba(255,255,255,0.12)" } },
    },
    visualMap: {
      min: domain.min,
      max: domain.max,
      calculable: true,
      orient: "horizontal",
      left: "center",
      bottom: 12,
      textStyle: { color: "#99b8b6" },
      formatter: visualMapFormatter(metric),
      inRange: { color: paletteForMetric(metric) },
    },
    series: [
      {
        type: "heatmap",
        data: values,
        label: {
          show: true,
          formatter: (params) => {
            const value = params.data.value[2];
            if (!isFiniteNumber(value)) return "";
            return metric === "premium_pct" ? percent.format(value) : formatCompactCurrency(value);
          },
          color: "#f3fbfb",
          fontSize: 10,
          fontWeight: 700,
          textShadowBlur: 8,
          textShadowColor: "rgba(0, 0, 0, 0.45)",
        },
        itemStyle: {
          borderRadius: 8,
          opacity: 0.98,
          borderColor: "rgba(255,255,255,0.12)",
          borderWidth: 1,
        },
      },
    ],
  };
}

function buildCondoScatterOption(rows, bucket) {
  const premiumDomain = metricDomain("premium_pct", rows);
  const points = rows
    .filter((row) => isFiniteNumber(row.listing_median) && isFiniteNumber(row.transaction_median))
    .map((row) => ({
      value: [row.transaction_median, row.listing_median, row.listing_count || 1],
      label: `D${row.district}`,
      row,
      itemStyle: { color: steppedColor(row.premium_pct, "premium_pct", premiumDomain) },
    }));
  const maxValue = Math.max(0, ...points.flatMap((point) => point.value.slice(0, 2)));

  return {
    backgroundColor: "transparent",
    animationDuration: 700,
    grid: { top: 18, right: 18, bottom: 54, left: 72 },
    tooltip: {
      backgroundColor: "rgba(7, 20, 27, 0.95)",
      borderColor: "rgba(255,255,255,0.08)",
      textStyle: { color: "#edf6f5" },
      formatter: (params) => {
        const row = params.data.row;
        const layoutLine =
          bucket === "2BR" && row.listing_layout_medians?.["2BR2BA"]
            ? `<br />2BR2BA 挂牌中位数: ${currency.format(row.listing_layout_medians["2BR2BA"])}`
            : "";
        return [
          `<strong>D${row.district} ${row.district_name}</strong>`,
          row.bedroom_bucket,
          `成交: ${currency.format(row.transaction_median)}`,
          `挂牌: ${currency.format(row.listing_median)}`,
          `溢价: ${formatMetric("premium_pct", row.premium_pct)}`,
          `挂牌量: ${row.listing_count}`,
          layoutLine,
        ].join("<br />");
      },
    },
    xAxis: {
      name: "Transaction Median",
      nameTextStyle: { color: "#99b8b6" },
      axisLabel: { color: "#c7d8d7", formatter: (value) => `$${Math.round(value / 1000)}k` },
      splitLine: { lineStyle: { color: "rgba(255,255,255,0.08)" } },
    },
    yAxis: {
      name: "Listing Median",
      nameTextStyle: { color: "#99b8b6" },
      axisLabel: { color: "#c7d8d7", formatter: (value) => `$${Math.round(value / 1000)}k` },
      splitLine: { lineStyle: { color: "rgba(255,255,255,0.08)" } },
    },
    series: [
      {
        type: "scatter",
        symbolSize: (value) => Math.max(10, Math.min(38, value[2] * 0.8)),
        data: points,
        label: {
          show: false,
          formatter: ({ data }) => data.label,
          color: "#dce9e8",
          position: "top",
        },
        emphasis: {
          label: {
            show: true,
            formatter: ({ data }) => data.label,
          },
        },
      },
      {
        type: "line",
        data: [
          [0, 0],
          [maxValue, maxValue],
        ],
        lineStyle: {
          color: "rgba(255,255,255,0.25)",
          type: "dashed",
        },
        symbol: "none",
        tooltip: { show: false },
      },
    ],
  };
}

function buildCondoRankingOption(rows, listingAvailable) {
  const ranked = listingAvailable
    ? [...rows]
        .filter((row) => isFiniteNumber(row.delta))
        .sort((a, b) => b.delta - a.delta)
    : [...rows]
        .filter((row) => isFiniteNumber(row.transaction_median))
        .sort((a, b) => b.transaction_median - a.transaction_median);
  const domain = metricDomain(listingAvailable ? "delta" : "transaction_median", ranked);

  return {
    backgroundColor: "transparent",
    animationDuration: 700,
    grid: { top: 18, right: 24, bottom: 32, left: 84 },
    tooltip: {
      backgroundColor: "rgba(7, 20, 27, 0.95)",
      borderColor: "rgba(255,255,255,0.08)",
      textStyle: { color: "#edf6f5" },
      formatter: (params) => {
        const row = ranked[params.dataIndex];
        return condoTooltipLines(row, listingAvailable).join("<br />");
      },
    },
    xAxis: {
      type: "value",
      axisLabel: { color: "#c7d8d7", formatter: (value) => `$${Math.round(value)}` },
      splitLine: { lineStyle: { color: "rgba(255,255,255,0.08)" } },
    },
    yAxis: {
      type: "category",
      data: ranked.map((row) => `D${row.district}`),
      axisLabel: { color: "#c7d8d7", interval: 0 },
    },
    series: [
      {
        type: "bar",
        data: ranked.map((row) => ({
          value: listingAvailable ? row.delta : row.transaction_median,
          itemStyle: {
            color: steppedColor(
              listingAvailable ? row.delta : row.transaction_median,
              listingAvailable ? "delta" : "transaction_median",
              domain,
            ),
          },
        })),
        barWidth: 16,
        label: {
          show: true,
          position: "right",
          color: "#edf6f5",
          formatter: ({ value }) => currency.format(value),
        },
      },
    ],
  };
}

function flattenGeometryVertices(geometry) {
  const vertices = [];
  if (!geometry) return vertices;
  const polygons = geometry.type === "Polygon" ? [geometry.coordinates] : geometry.coordinates || [];
  for (const polygon of polygons) {
    for (const ring of polygon) {
      for (const [longitude, latitude] of ring) {
        vertices.push([longitude, latitude]);
      }
    }
  }
  return vertices;
}

function featureCenter(feature) {
  const vertices = flattenGeometryVertices(feature.geometry);
  if (!vertices.length) return [103.8198, 1.3521];
  const [sumLon, sumLat] = vertices.reduce(
    (acc, [longitude, latitude]) => [acc[0] + longitude, acc[1] + latitude],
    [0, 0],
  );
  return [sumLon / vertices.length, sumLat / vertices.length];
}

function buildCondoMapOption(districtGeoJSON, districtPoints, districtRows, metric, listingAvailable) {
  if (!districtGeoJSON?.features?.length) {
    return {
      title: {
        text: "Map data unavailable",
        left: "center",
        top: "middle",
        textStyle: { color: "#99b8b6", fontWeight: 400 },
      },
      backgroundColor: "transparent",
    };
  }

  const domain = metricDomain(metric, districtRows);
  const rowMap = new Map(districtRows.map((row) => [row.district, row]));
  const districtData = districtRows.map((row) => ({
    name: row.district,
    district: row.district,
    district_name: row.district_name,
    value: row?.[metric] ?? null,
    transaction_median: row?.transaction_median ?? null,
    listing_median: row?.listing_median ?? null,
    delta: row?.delta ?? null,
    premium_pct: row?.premium_pct ?? null,
    transaction_count: row?.transaction_count ?? null,
    listing_count: row?.listing_count ?? null,
  }));

  const pointFallbackMap = new Map(
    (districtPoints || []).map((point) => [point.district, [point.longitude, point.latitude]]),
  );
  const districtFeatureMap = new Map(
    (districtGeoJSON.features || []).map((feature) => [feature.properties?.district, feature]),
  );

  const scatterData = districtRows
    .filter((row) => rowMap.has(row.district))
    .map((row) => {
      const coordinate =
        pointFallbackMap.get(row.district)
        || districtLabelOverrides[row.district]
        || (districtFeatureMap.get(row.district) ? featureCenter(districtFeatureMap.get(row.district)) : null);
      if (!coordinate) return null;
      return {
        name: `D${row.district}`,
        district: row.district,
        district_name: row.district_name,
        transaction_median: row.transaction_median,
        listing_median: row.listing_median,
        delta: row.delta,
        premium_pct: row.premium_pct,
        transaction_count: row.transaction_count,
        listing_count: row.listing_count,
        value: [coordinate[0], coordinate[1], row[metric] ?? null],
      };
    })
    .filter(Boolean);

  return {
    backgroundColor: "transparent",
    animationDuration: 700,
    tooltip: {
      backgroundColor: "rgba(7, 20, 27, 0.95)",
      borderColor: "rgba(255,255,255,0.08)",
      textStyle: { color: "#edf6f5" },
      formatter: (params) => {
        if (params.seriesType === "map") {
          const row = params.data || {};
          return condoTooltipLines(row, listingAvailable).join("<br />");
        }
        const row = params.data || {};
        return condoTooltipLines(row, listingAvailable).join("<br />");
      },
    },
    visualMap: {
      min: domain.min,
      max: domain.max,
      seriesIndex: 0,
      calculable: true,
      orient: "vertical",
      right: 6,
      top: "middle",
      text: [metricLabels[metric], ""],
      textStyle: { color: "#99b8b6" },
      formatter: visualMapFormatter(metric),
      inRange: { color: paletteForMetric(metric) },
    },
    geo: {
      map: "sg-districts",
      roam: true,
      nameProperty: "name",
      left: 8,
      right: 80,
      top: 12,
      bottom: 12,
      itemStyle: {
        areaColor: "rgba(23, 44, 56, 0.85)",
        borderColor: "rgba(219, 239, 237, 0.18)",
        borderWidth: 1,
      },
      emphasis: {
        itemStyle: {
          borderColor: "rgba(255,255,255,0.6)",
          borderWidth: 1.2,
        },
        label: { show: false },
      },
      label: { show: false },
    },
    series: [
      {
        type: "map",
        map: "sg-districts",
        geoIndex: 0,
        nameProperty: "name",
        data: districtData,
      },
      {
        type: "scatter",
        coordinateSystem: "geo",
        data: scatterData,
        symbolSize: (value, params) => {
          const samples = Math.max(params.data.transaction_count || 0, params.data.listing_count || 0);
          return Math.max(12, Math.min(30, 12 + samples * 0.15));
        },
        itemStyle: {
          borderColor: "rgba(255,255,255,0.9)",
          borderWidth: 1.3,
          shadowBlur: 16,
          shadowColor: "rgba(0, 0, 0, 0.32)",
          color: (params) => steppedColor(params.data.value[2], metric, domain),
        },
        label: {
          show: true,
          formatter: ({ data }) => `D${data.district}`,
          color: "#f6fbfb",
          fontWeight: 700,
          fontSize: 10,
          textShadowBlur: 8,
          textShadowColor: "rgba(0, 0, 0, 0.45)",
          position: "inside",
        },
      },
    ],
  };
}

function buildHdbTreemapOption(rows) {
  const filtered = rows.filter((row) => isFiniteNumber(row.median_rent) && (row.approval_count || 0) > 0);
  const domain = metricDomain("median_rent", filtered);
  return {
    backgroundColor: "transparent",
    tooltip: {
      backgroundColor: "rgba(7, 20, 27, 0.95)",
      borderColor: "rgba(255,255,255,0.08)",
      textStyle: { color: "#edf6f5" },
      formatter: (params) => {
        const row = params.data;
        return [
          `<strong>${row.town}</strong>`,
          `中位租金: ${formatMetric("median_rent", row.median_rent)}`,
          `样本量: ${row.approval_count}`,
        ].join("<br />");
      },
    },
    series: [
      {
        type: "treemap",
        roam: false,
        breadcrumb: { show: false },
        nodeClick: false,
        itemStyle: {
          borderColor: "rgba(255,255,255,0.12)",
          borderWidth: 1,
          gapWidth: 4,
        },
        upperLabel: { show: false },
        label: {
          show: true,
          formatter: ({ data }) => `${data.town}\n${formatCompactCurrency(data.median_rent)}`,
          color: "#edf6f5",
          fontWeight: 700,
          lineHeight: 18,
        },
        data: filtered.map((row) => ({
          name: row.town,
          town: row.town,
          approval_count: row.approval_count,
          median_rent: row.median_rent,
          value: Math.max(1, row.approval_count || 1),
          itemStyle: {
            color: steppedColor(row.median_rent, "median_rent", domain),
          },
        })),
      },
    ],
  };
}

function buildHdbHeatmapOption(rows) {
  const flatTypes = [...new Set(rows.map((row) => row.flat_type))];
  const towns = [...new Set(rows.map((row) => row.town))];
  const domain = metricDomain("median_rent", rows);
  const values = rows.map((row) => ({
    value: [
      flatTypes.indexOf(row.flat_type),
      towns.indexOf(row.town),
      row.median_rent,
    ],
    row,
  }));

  return {
    backgroundColor: "transparent",
    animationDuration: 700,
    grid: { top: 18, right: 12, bottom: 70, left: 140 },
    tooltip: {
      confine: true,
      backgroundColor: "rgba(7, 20, 27, 0.95)",
      borderColor: "rgba(255,255,255,0.08)",
      textStyle: { color: "#edf6f5" },
      formatter: (params) => {
        const row = params.data.row;
        return [
          `<strong>${row.town}</strong>`,
          row.flat_type,
          `中位租金: ${formatMetric("median_rent", row.median_rent)}`,
          `样本量: ${row.approval_count || 0}`,
        ].join("<br />");
      },
    },
    xAxis: {
      type: "category",
      data: flatTypes,
      axisLabel: { color: "#c7d8d7" },
      axisLine: { lineStyle: { color: "rgba(255,255,255,0.12)" } },
    },
    yAxis: {
      type: "category",
      inverse: true,
      data: towns,
      axisLabel: { color: "#c7d8d7", interval: 0, margin: 14 },
      axisLine: { lineStyle: { color: "rgba(255,255,255,0.12)" } },
    },
    visualMap: {
      min: domain.min,
      max: domain.max,
      calculable: true,
      orient: "horizontal",
      left: "center",
      bottom: 12,
      textStyle: { color: "#99b8b6" },
      formatter: visualMapFormatter("median_rent"),
      inRange: { color: paletteForMetric("median_rent") },
    },
    series: [
      {
        type: "heatmap",
        data: values,
        label: {
          show: true,
          formatter: (params) => {
            const value = params.data.value[2];
            return isFiniteNumber(value) ? formatCompactCurrency(value) : "";
          },
          color: "#f3fbfb",
          fontSize: 10,
          fontWeight: 700,
          textShadowBlur: 8,
          textShadowColor: "rgba(0, 0, 0, 0.45)",
        },
        itemStyle: {
          borderRadius: 8,
          opacity: 0.98,
          borderColor: "rgba(255,255,255,0.12)",
          borderWidth: 1,
        },
      },
    ],
  };
}

function buildHdbRankingOption(rows) {
  const ranked = [...rows]
    .filter((row) => isFiniteNumber(row.median_rent))
    .sort((a, b) => b.median_rent - a.median_rent);
  const domain = metricDomain("median_rent", ranked);

  return {
    backgroundColor: "transparent",
    animationDuration: 700,
    grid: { top: 18, right: 24, bottom: 32, left: 130 },
    tooltip: {
      backgroundColor: "rgba(7, 20, 27, 0.95)",
      borderColor: "rgba(255,255,255,0.08)",
      textStyle: { color: "#edf6f5" },
      formatter: (params) => {
        const row = ranked[params.dataIndex];
        return [
          `<strong>${row.town}</strong>`,
          `中位租金: ${formatMetric("median_rent", row.median_rent)}`,
          `样本量: ${row.approval_count || 0}`,
        ].join("<br />");
      },
    },
    xAxis: {
      type: "value",
      axisLabel: { color: "#c7d8d7", formatter: (value) => `$${Math.round(value)}` },
      splitLine: { lineStyle: { color: "rgba(255,255,255,0.08)" } },
    },
    yAxis: {
      type: "category",
      data: ranked.map((row) => row.town),
      axisLabel: { color: "#c7d8d7", interval: 0 },
    },
    series: [
      {
        type: "bar",
        data: ranked.map((row) => ({
          value: row.median_rent,
          itemStyle: { color: steppedColor(row.median_rent, "median_rent", domain) },
        })),
        barWidth: 16,
        label: {
          show: true,
          position: "right",
          color: "#edf6f5",
          formatter: ({ value }) => currency.format(value),
        },
      },
    ],
  };
}

function animateIn() {
  if (!window.gsap) return;
  window.gsap.from(".panel", {
    y: 18,
    opacity: 0,
    stagger: 0.08,
    duration: 0.65,
    ease: "power2.out",
  });
}

async function main() {
  const snapshot = await loadFirstAvailable(SNAPSHOT_SOURCES);
  const districtBoundaryGeoJSON = await loadOptional(DISTRICT_BOUNDARY_SOURCES);
  const districtLabelPointsPayload = await loadOptional(DISTRICT_LABEL_POINT_SOURCES);
  const planningAreaGeoJSON = districtBoundaryGeoJSON ? null : await loadOptional(PLANNING_AREA_SOURCES);
  const districtPointsPayload = districtLabelPointsPayload ? null : await loadOptional(DISTRICT_POINT_SOURCES);
  const districtPoints = districtLabelPointsPayload?.records || districtPointsPayload?.records || [];
  const districtGeoJSON = districtBoundaryGeoJSON || buildDistrictGeoJSON(planningAreaGeoJSON);
  if (districtGeoJSON?.features?.length) {
    echarts.registerMap("sg-districts", districtGeoJSON);
  }

  const condoListingAvailable = hasCondoListingData(snapshot);
  const condoBuckets = snapshot.condo?.bedroom_buckets || [];
  const hdbFlatTypes = snapshot.hdb?.flat_types || [];

  const state = {
    market: "condo",
    condoBucket: "all",
    hdbFlatType: "all",
    metric: "transaction_median",
  };

  const heroText = document.getElementById("hero-text");
  const condoBucketSelect = document.getElementById("condo-bucket-select");
  const hdbFlatSelect = document.getElementById("hdb-flat-select");
  const metricSelect = document.getElementById("metric-select");

  heroText.textContent = CONDO_COPY.hero;

  for (const bucket of condoBuckets) {
    const option = document.createElement("option");
    option.value = bucket;
    option.textContent = bucket;
    condoBucketSelect.appendChild(option);
  }

  for (const flatType of hdbFlatTypes) {
    const option = document.createElement("option");
    option.value = flatType;
    option.textContent = flatType;
    hdbFlatSelect.appendChild(option);
  }

  const contextChart = echarts.init(document.getElementById("context-chart"));
  const heatmapChart = echarts.init(document.getElementById("heatmap"));
  const scatterChart = echarts.init(document.getElementById("scatter"));
  const rankingChart = echarts.init(document.getElementById("ranking"));

  function renderCondo() {
    const rows = getCondoRows(snapshot, state.condoBucket);
    const districtRows = getCondoDistrictComparison(rows, state.condoBucket, condoListingAvailable);
    const metricRows = state.condoBucket === "all"
      ? districtRows
      : filterReliableCondoRows(rows, condoListingAvailable);
    const totalDistrictCount = new Set((snapshot.condo?.districts || []).map((row) => row.district)).size;
    setChartHeights("condo", rows, districtRows);
    renderMetrics(condoMetrics(metricRows, condoListingAvailable, snapshot.meta, totalDistrictCount));
    contextChart.setOption(
      buildCondoMapOption(districtGeoJSON, districtPoints, districtRows, state.metric, condoListingAvailable),
      true,
    );
    heatmapChart.setOption(buildCondoHeatmapOption(rows, state.metric, condoListingAvailable), true);
    if (condoListingAvailable) {
      scatterChart.setOption(buildCondoScatterOption(districtRows, state.condoBucket), true);
    } else {
      scatterChart.clear();
    }
    rankingChart.setOption(buildCondoRankingOption(districtRows, condoListingAvailable), true);
  }

  function renderHdb() {
    const rows = getHdbRows(snapshot, state.hdbFlatType);
    const townRows = getHdbTownComparison(rows, state.hdbFlatType);
    setChartHeights("hdb", rows, townRows);
    renderMetrics(hdbMetrics(townRows, snapshot.meta, (snapshot.hdb?.town_names || []).length));
    contextChart.setOption(buildHdbTreemapOption(townRows), true);
    heatmapChart.setOption(buildHdbHeatmapOption(rows), true);
    rankingChart.setOption(buildHdbRankingOption(townRows), true);
    scatterChart.clear();
  }

  function render() {
    if (!condoListingAvailable && state.metric !== "transaction_median") {
      state.metric = "transaction_median";
      metricSelect.value = "transaction_median";
    }
    renderMarketTabs(state.market);
    renderControls(state.market, condoListingAvailable);
    renderModeCopy(state.market, condoListingAvailable);
    renderStatus(snapshot);

    if (state.market === "condo") {
      renderCondo();
    } else {
      renderHdb();
    }

    contextChart.resize();
    heatmapChart.resize();
    scatterChart.resize();
    rankingChart.resize();
  }

  document.querySelectorAll(".market-tab").forEach((button) => {
    button.addEventListener("click", () => {
      state.market = button.dataset.market;
      render();
    });
  });

  condoBucketSelect.addEventListener("change", () => {
    state.condoBucket = condoBucketSelect.value;
    render();
  });

  hdbFlatSelect.addEventListener("change", () => {
    state.hdbFlatType = hdbFlatSelect.value;
    render();
  });

  metricSelect.addEventListener("change", () => {
    state.metric = metricSelect.value;
    render();
  });

  window.addEventListener("resize", () => {
    contextChart.resize();
    heatmapChart.resize();
    scatterChart.resize();
    rankingChart.resize();
  });

  render();
  animateIn();
}

main().catch((error) => {
  const status = document.getElementById("dataset-status");
  status.textContent = `Failed to load dashboard data: ${error.message}`;
});
