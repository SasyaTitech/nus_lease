# Lion City Rent Atlas

Public dashboard for reading Singapore rents by district, by town, and by flat type.

Chinese README:
- [README.md](README.md)

Live site:
- https://sasyatitech.github.io/nus_lease/

Repository:
- https://github.com/SasyaTitech/nus_lease

If this project is helpful, please consider giving it a star:
- https://github.com/SasyaTitech/nus_lease

Built and maintained by:
- Sasya / https://github.com/SasyaTitech

`nus_lease` remains the internal package and repository name. `Lion City Rent Atlas` is the public-facing project name.

## What You Can Explore

The dashboard currently has two views:

- `Condo`
  - district-level private rental prices
  - bedroom-bucket heatmaps
  - district ranking and coverage
  - asking-vs-transaction comparisons when listing data is available
- `HDB`
  - town-level HDB rental view
  - flat-type heatmaps
  - town ranking based on official approvals

## Data Transparency

### Condo transactions

Condo transaction data comes from URA's private residential rental contract data.

Official references:
- URA rental search: https://eservice.ura.gov.sg/property-market-information/pmiResidentialRentalSearch
- URA API portal: https://eservice.ura.gov.sg/maps/api/

Key caveats:
- it is an official source for private residential rental contracts
- it covers private residential rentals submitted to `IRAS` for stamp duty assessment
- it does not cover `HDB`
- bedroom counts are useful for `non-landed` records, but some records still have missing bedroom information
- bathroom counts are not provided by URA

### HDB rents

HDB data comes from the official open dataset for renting out flats.

Official source:
- https://data.gov.sg/datasets/d_c9f57187485a850908655db0e8cfe651/view

### Map geometry

The district map is a `D01-D28` proxy layer assembled from public URA planning-area boundaries, not an official postal-district polygon file.

Official boundary source:
- https://data.gov.sg/datasets/d_2cc750190544007400b2cfd5d7f53209/view

## What Is Public In This Repo

The public repository keeps only what the website needs to render:

- `web/`
- `data/processed/market_snapshot.json`
- `data/fixtures/demo_market_snapshot.json`
- `data/raw/planning_area_boundaries.geojson`
- `data/raw/district_centroids.json`

Local raw exports such as URA pulls, HDB pulls, browser-exported listing HTML, and caches are ignored by default.

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

```bash
export URA_ACCESS_KEY='your-access-key'
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

Output:

- `data/processed/market_snapshot.json`

## Optional Asking-Rent Pipeline

### Parse browser-exported listing HTML

```bash
python3 scripts/import_propertyguru_html.py
```

Expected input:

- `data/raw/propertyguru_html/`

Expected output:

- `data/raw/propertyguru_listings.json`

### Attempt Playwright-based fetch

```bash
python3 -m playwright install chromium
python3 scripts/fetch_propertyguru_live.py \
  --url 'https://www.propertyguru.com.sg/apartment-condo-for-rent/in-singapore'
```

This route may fail if the site returns a challenge page.

## Deploy

This repository already includes a GitHub Pages workflow:

- [.github/workflows/deploy-pages.yml](.github/workflows/deploy-pages.yml)

If you fork the repo, enable `GitHub Pages` with `GitHub Actions` as the source and push to `main`.

## Contributing

Issues, data-source suggestions, geometry fixes, and UI improvements are welcome.

If this project helped you, a star would mean a lot:
- https://github.com/SasyaTitech/nus_lease
