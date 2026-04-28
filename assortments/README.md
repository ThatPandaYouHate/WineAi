# Assortments data

This folder is intentionally empty in git. It is meant to contain Systembolaget
data files that are too large to commit (~1.5 GB):

- `stores.json` — list of all non-agent stores
- `<siteId>.json` — full wine assortment for each store (one file per store)

## How to populate

The data is fetched via the helper script in `../scripts/update_data.py`,
which expects an SSH-reachable copy of the
[`systembolaget` CLI](https://github.com/AlexGustafsson/systembolaget-api):

```sh
cd ..
python scripts/update_data.py
```

Edit the script if your remote/binary path differs.

## Format reminder

Each `<siteId>.json` is a JSON array of product objects with at least the
following fields used by the backend (`backend/app/services/assortment.py`):

`productNumber`, `productNameBold`, `productNameThin`, `producerName`,
`vintage`, `country`, `originLevel1`, `categoryLevel2`, `categoryLevel3`,
`assortmentText`, `price`, `volume`, `alcoholPercentage`,
`productLaunchDate`, `isCompletelyOutOfStock`, `isTemporaryOutOfStock`.
