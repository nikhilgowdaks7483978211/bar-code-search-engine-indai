from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx
import os
import re
from typing import Optional

APP_NAME = "Barcode Intelligence India"
OFF_BASE = "https://world.openfoodfacts.org"
TIMEOUT = 12.0

app = FastAPI(title=APP_NAME, version="1.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

def clean_text(value):
    if value is None:
        return None
    if isinstance(value, list):
        return ", ".join(str(x) for x in value if x)
    value = str(value).strip()
    return value or None

def normalize_product(raw: dict, barcode: Optional[str] = None):
    nutriments = raw.get("nutriments") or {}
    def n(key):
        value = nutriments.get(key)
        return value if value not in ("", None) else None

    return {
        "name": clean_text(raw.get("product_name") or raw.get("product_name_en")) or "Name not available",
        "brand": clean_text(raw.get("brands")),
        "barcode": clean_text(raw.get("code") or barcode),
        "image": raw.get("image_front_url") or raw.get("image_url"),
        "quantity": clean_text(raw.get("quantity")),
        "categories": clean_text(raw.get("categories")),
        "ingredients": clean_text(raw.get("ingredients_text") or raw.get("ingredients_text_en")),
        "allergens": clean_text(raw.get("allergens")),
        "labels": clean_text(raw.get("labels")),
        "country": clean_text(raw.get("countries")),
        "nutrition_per_100g": {
            "energy_kcal": n("energy-kcal_100g") or n("energy-kcal"),
            "fat_g": n("fat_100g"),
            "saturated_fat_g": n("saturated-fat_100g"),
            "carbohydrates_g": n("carbohydrates_100g"),
            "sugars_g": n("sugars_100g"),
            "proteins_g": n("proteins_100g"),
            "salt_g": n("salt_100g"),
            "sodium_mg": n("sodium_100g"),
        },
        "data_source": "Open Food Facts",
        "source_url": f"https://world.openfoodfacts.org/product/{raw.get('code') or barcode}" if (raw.get("code") or barcode) else "https://world.openfoodfacts.org/",
        "hsn_code": None,
        "gst_rate": None,
        "price": None,
        "retailer_search": None,
    }

async def off_get(path: str, params=None):
    headers = {"User-Agent": "BarcodeIntelligenceIndia/1.0 (educational product lookup app)"}
    async with httpx.AsyncClient(timeout=TIMEOUT, headers=headers, follow_redirects=True) as client:
        response = await client.get(f"{OFF_BASE}{path}", params=params)
        response.raise_for_status()
        return response.json()

@app.get("/")
async def home():
    return FileResponse("static/index.html")

@app.get("/api/health")
async def health():
    return {"status": "ok", "app": APP_NAME, "version": "1.0.0"}

@app.get("/api/barcode/{code}")
async def barcode_lookup(code: str):
    code = re.sub(r"\s+", "", code)
    if not code.isdigit() or not (8 <= len(code) <= 14):
        raise HTTPException(status_code=400, detail="Enter a valid 8–14 digit barcode.")
    try:
        payload = await off_get(f"/api/v2/product/{code}.json")
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Product database is temporarily unavailable. Please try again.")
    if payload.get("status") != 1 or not payload.get("product"):
        raise HTTPException(status_code=404, detail="No product record found for this barcode. Try searching by product name.")
    product = normalize_product(payload["product"], code)
    product["retailer_search"] = f"https://www.google.com/search?tbm=shop&q={code}"
    return {"found": True, "product": product}

@app.get("/api/search")
async def search_products(q: str = Query(..., min_length=2, max_length=100), page: int = 1):
    q = q.strip()
    try:
        payload = await off_get("/cgi/search.pl", {
            "search_terms": q,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": 24,
            "page": max(1, min(page, 20)),
            "fields": "code,product_name,product_name_en,brands,image_front_url,image_url,quantity,categories,countries"
        })
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Product database is temporarily unavailable. Please try again.")
    products = [normalize_product(p) for p in payload.get("products", [])]
    products = [p for p in products if p.get("barcode") or p.get("name") != "Name not available"]
    return {"query": q, "count": len(products), "products": products, "page": page}

@app.get("/api/retailer-search/{code}")
async def retailer_search(code: str):
    if not code.isdigit():
        raise HTTPException(status_code=400, detail="Barcode must contain digits only.")
    return {"search_url": f"https://www.google.com/search?tbm=shop&q={code}"}
