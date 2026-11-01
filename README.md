# Barcode Intelligence India

A mobile-friendly barcode and product-name lookup web application. It uses the public Open Food Facts database for product records.

## Features
- Search by barcode (8–14 digits) or product name.
- Search using a phone camera barcode scanner (HTTPS required).
- Display available brand, quantity, image, categories, ingredients, allergens, labels and nutrition facts.
- Link to the source record and a retailer search page.
- Responsive dark interface.
- FastAPI backend with health endpoint and Docker deployment configuration.

## Important data limitations
This starter version does **not** have a verified, complete Indian product catalogue. Open Food Facts coverage varies by product and region, and records may be missing or community-contributed. A barcode can be valid even when no record is found.

Live prices, retailer stock, HSN codes and GST rates are not supplied by the integrated database. The app deliberately labels these as unavailable rather than inventing values. Do not use it for tax classification or safety-critical decisions without checking authoritative sources and the package.

## Run locally on Windows

1. Install Python 3.10+ from https://www.python.org/downloads/
2. Extract this ZIP file.
3. Open the extracted `barcode_intelligence_india` folder.
4. Click the address bar in File Explorer, type `cmd`, and press Enter.
5. Run:

   ```bat
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

6. Open Chrome and visit http://127.0.0.1:8000

If `py` is unavailable, use `python` instead. Camera scanning generally requires HTTPS; manual barcode entry works locally.

## Deploy publicly with Render

1. Create a GitHub repository named `search-engine-barcode` (or use your existing repository).
2. Extract this ZIP.
3. Upload the **contents** of the extracted folder to the root of your GitHub repository. The `app`, `static`, `Dockerfile`, `render.yaml`, and `requirements.txt` files must be at the repository root.
4. Commit the files to the `main` branch.
5. Sign in to https://render.com
6. Choose **New + → Blueprint** and connect your GitHub repository.
7. Render detects `render.yaml`. Review and create the web service.
8. When deployment completes, open the `onrender.com` URL shown in the Render dashboard.

The free hosting plan and free database/API coverage can change. The service may sleep when idle and take a little time to wake up.

## API endpoints
- `GET /api/health`
- `GET /api/barcode/{code}`
- `GET /api/search?q={product name}`
- `GET /api/retailer-search/{code}`

## Data source
Open Food Facts: https://world.openfoodfacts.org/
API documentation: https://openfoodfacts.github.io/openfoodfacts-server/api/
