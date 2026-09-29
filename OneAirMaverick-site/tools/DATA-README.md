# Map and airport data

Both files are generated from public-domain sources. No credit or license is required, and the site calls no outside service for the map or search.

- `public/assets/data/airports.js`: public-use airports in the U.S. and the Caribbean with a paved runway of at least 2,500 ft, plus a few island strips charter aircraft use (St. Barts, Negril, Union Island). Military-only bases and private-use strips are excluded. Joint civil-military fields are kept. Cuba is left out because U.S. travel there is restricted. Source: OurAirports (https://ourairports.com/data/), public domain.
- `public/assets/data/map-data.js`: country shapes, U.S. state lines, lakes and city labels. Source: Natural Earth (https://www.naturalearthdata.com), public domain.

## Refreshing the data (about once a year)

In an empty folder:

1. Download `airports.csv` and `runways.csv` from https://davidmegginson.github.io/ourairports-data/
2. Download from https://github.com/nvkelso/natural-earth-vector/tree/master/geojson:
   `ne_10m_admin_0_countries`, `ne_10m_admin_1_states_provinces_lines`, `ne_10m_lakes`, `ne_10m_populated_places_simple` (.geojson)
3. Clip and simplify with mapshaper (`npm i mapshaper`):
   ```
   npx mapshaper ne_10m_admin_0_countries.geojson -clip bbox=-180,5,-50,72 -simplify 6% keep-shapes -filter-fields ADM0_A3,NAME,LABEL_X,LABEL_Y,MIN_LABEL -o countries.geojson precision=0.0005
   npx mapshaper ne_10m_admin_1_states_provinces_lines.geojson -filter 'ADM0_A3=="USA" || ADM0_A3=="CAN" || ADM0_A3=="MEX"' -clip bbox=-180,5,-50,72 -simplify 6% -filter-fields ADM0_A3 -o states.geojson precision=0.0005
   npx mapshaper ne_10m_lakes.geojson -filter 'scalerank<=3' -clip bbox=-180,5,-50,72 -simplify 8% keep-shapes -filter-fields name -o lakes.geojson precision=0.0005
   ```
4. From that folder, run `python3 path/to/tools/airports.py 2500` (the number is the minimum paved runway length in feet), then `python3 path/to/tools/build.py`. The build writes both files into `public/assets/data/`.
