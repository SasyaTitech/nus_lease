# Lion City Rent Atlas

Public dashboard for reading Singapore rents by district, by town, and by flat type.

Live site:
- https://sasyatitech.github.io/nus_lease/

Repository:
- https://github.com/SasyaTitech/nus_lease

If this project is useful, please star the repo:
- https://github.com/SasyaTitech/nus_lease

Built and maintained by:
- Sasya / https://github.com/SasyaTitech

`nus_lease` remains the internal package/repository name. `Lion City Rent Atlas` is the public-facing project name.

## What You Can Explore

The dashboard currently has two views:

- `Condo`
  - District-level private rental prices
  - Bedroom-bucket heatmaps
  - District ranking and coverage
  - When listing data is available, asking vs transaction comparisons
- `HDB`
  - Town-level HDB rental view
  - Flat-type heatmaps
  - Town ranking based on official approvals

The public site is designed for readers first: open it, switch between `Condo` and `HDB`, then narrow by bedroom bucket or flat type.

## Data Transparency

### Condo transactions

Condo transaction data comes from URA's private residential rental contract data.

Official references:
- URA rental search: https://eservice.ura.gov.sg/property-market-information/pmiResidentialRentalSearch
- URA API portal: https://eservice.ura.gov.sg/maps/api/

What that means:
- It is an official source for private residential rental contracts.
- It covers private residential rentals submitted to `IRAS` for stamp duty assessment.
- It does not cover `HDB`.
- Bedroom counts are useful for `non-landed` records, but some records are still missing bedroom information.
- Bathroom counts are not provided by URA.

### HDB rents

HDB data comes from the official open dataset for renting out flats.

Official source:
- https://data.gov.sg/datasets/d_c9f57187485a850908655db0e8cfe651/view

What that means:
- This is an official HDB rental-approval style dataset.
- The dashboard aggregates recent records into `town x flat type`.

### Boundaries and map geometry

The district map is not a perfect official postal-district polygon layer.

It is built from public URA planning-area boundaries and merged into a `D01-D28` proxy layer.

Official boundary source:
- https://data.gov.sg/datasets/d_2cc750190544007400b2cfd5d7f53209/view

So the map is good for market reading and comparison, but should not be treated as a legal cadastral boundary product.

### Asking rents

The codebase includes an optional PropertyGuru adapter for asking-rent snapshots, but the public site may not always expose this layer.

That is because:
- asking rents are not the same thing as closed deals
- listing pages can be blocked by anti-bot systems
- public listing coverage is inherently less stable than official contract data

## What Is Public In This Repo

The public repository keeps only what the website needs to render:

- `web/`
- `data/processed/market_snapshot.json`
- `data/fixtures/demo_market_snapshot.json`
- `data/raw/planning_area_boundaries.geojson`
- `data/raw/district_centroids.json`

The repository is configured to ignore local raw exports such as:

- URA raw pulls
- HDB raw pulls
- PropertyGuru HTML exports
- local caches and build junk

See:
- [.gitignore](.gitignore)

## Run Locally

```bash
python3 -m pip install -e .
python3 -m http.server 8000
```

Then open:

- http://localhost:8000/web/

## Generate Fresh Data

### 1. Fetch public boundary helpers

```bash
python3 scripts/fetch_planning_area_boundaries.py
python3 scripts/fetch_district_centroids.py
```

### 2. Fetch URA condo transactions

First export your URA access key:

```bash
export URA_ACCESS_KEY='your-access-key'
```

Then fetch recent condo rental contracts:

```bash
python3 scripts/fetch_ura_private_rentals.py --months 6
```

Output:

- `data/raw/ura_private_rentals.json`

### 3. Fetch HDB rental data

```bash
python3 scripts/fetch_hdb_rentals.py --months 3
```

Output:

- `data/raw/hdb_rentals.json`

### 4. Build the dashboard snapshot

```bash
python3 scripts/build_market_snapshot.py --hdb data/raw/hdb_rentals.json
```

Outputs:

- `data/processed/market_snapshot.json`
- `data/fixtures/demo_market_snapshot.json` if you separately build demo data

## Optional: Asking-Rent Pipeline

If you want to extend the project with asking-rent snapshots:

### Parse browser-exported listing HTML

```bash
python3 scripts/import_propertyguru_html.py
```

Expected input directory:

- `data/raw/propertyguru_html/`

Expected output:

- `data/raw/propertyguru_listings.json`

### Attempt Playwright-based fetch

```bash
python3 -m playwright install chromium
python3 scripts/fetch_propertyguru_live.py \
  --url 'https://www.propertyguru.com.sg/apartment-condo-for-rent/in-singapore'
```

This path may fail if the site returns a challenge page.

## Deploy

This repo already includes a GitHub Pages workflow:

- [.github/workflows/deploy-pages.yml](.github/workflows/deploy-pages.yml)

By default it publishes:

- `web/`
- `data/processed/market_snapshot.json`
- `data/fixtures/demo_market_snapshot.json`
- `data/raw/planning_area_boundaries.geojson`
- `data/raw/district_centroids.json`

If you fork the repo, enable `GitHub Pages` with `GitHub Actions` as the source and push to `main`.

## Contributing

Issues, data-source suggestions, geometry fixes, and UI improvements are welcome.

If you found the project useful, a star helps a lot:
- https://github.com/SasyaTitech/nus_lease
