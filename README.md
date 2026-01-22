# Zcash Shielded Pool Tracker 🔒

Automatically fetches Zcash shielded pool data every 8 hours via GitHub Actions.

## Data

The `shielded_data.json` file contains historical data with:
- `date` - Date (YYYY-MM-DD)
- `timestamp` - Full ISO timestamp
- `sprout` - Sprout pool balance (ZEC)
- `sapling` - Sapling pool balance (ZEC)  
- `orchard` - Orchard pool balance (ZEC)
- `total` - Total shielded (ZEC)

## Setup

1. **Fork or clone this repo**

2. **Enable GitHub Actions**
   - Go to repo Settings → Actions → General
   - Select "Allow all actions"

3. **Run manually (first time)**
   - Go to Actions tab
   - Click "Update Shielded Pool Data"
   - Click "Run workflow"

4. **Automatic updates**
   - Runs automatically at 00:00, 08:00, 16:00 UTC
   - Data commits directly to the repo

## Use in your website

Fetch the raw JSON from GitHub:

```javascript
const DATA_URL = 'https://raw.githubusercontent.com/YOUR_USERNAME/zcash-shielded-tracker/main/shielded_data.json';

async function fetchShieldedData() {
  const response = await fetch(DATA_URL);
  return await response.json();
}
```

## Data source

Data scraped from [mainnet.zcashexplorer.app](https://mainnet.zcashexplorer.app/blockchain-info)

---

Built with 💛 for the Zcash community
