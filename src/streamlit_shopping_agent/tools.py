from agents import function_tool
from typing import List, Dict, Any, Annotated
import os, json, gspread, tempfile

# Attempt to load credentials from environment, else fallback to file
CREDENTIALS_ENV = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
CREDENTIALS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../gc.json")
)

@function_tool
async def search_products(
    query: Annotated[str, "Search term to find products"],
) -> Dict[str, Any]:
    """
    Search for products in the Google Sheet based on query,
    return a dict with products, recommended_products, message.
    """
    print(f"🔍 [search_products] Received query: `{query}`")
    try:
        # Initialize gspread client
        if CREDENTIALS_ENV:
            creds_dict = json.loads(CREDENTIALS_ENV)
            gc = gspread.service_account_from_dict(creds_dict)
            print("🔑 [search_products] Loaded credentials from env var.")
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(f"Credentials file not found at {CREDENTIALS_PATH}")
            gc = gspread.service_account(filename=CREDENTIALS_PATH)
            print(f"🔑 [search_products] Loaded credentials from file {CREDENTIALS_PATH}.")

        sheet = gc.open("FurnitureProducts").sheet1
        products = sheet.get_all_records()
        print(f"🗄️  [search_products] Fetched {len(products)} rows from sheet.")

        # Normalize name and category fields for better matching
        for p in products:
            p["name"] = p.get("name", "").strip().lower()
            p["category"] = p.get("category", "").strip().lower()

        # Build variations for matching
        query_words = [w.strip().lower() for w in query.split()]
        query_variations = []
        for w in query_words:
            query_variations.append(w)
            if w.endswith("s"):
                query_variations.append(w[:-1])
            else:
                query_variations.append(w + "s")

        # Find matches in name OR category
        matching = []
        for p in products:
            name = p["name"]
            cat = p["category"]
            if any(var in name for var in query_variations) or any(var in cat for var in query_variations):
                matching.append(p)
        print(f"✅ [search_products] Matched {len(matching)} products: {[p['name'] for p in matching]}")

        # If no matches, early return
        if not matching:
            return {
                "products": [],
                "recommended_products": [],
                "message": "No matching products found."
            }

        # Recommend other items in same categories
        cats = {p["category"].strip() for p in matching}
        recommended = [
            p for p in products
            if p.get("category", "").strip() in cats and p not in matching
        ]
        print(f"🎁 [search_products] Recommended {len(recommended)} products: {[p['name'] for p in recommended]}")

        return {
            "products": matching,
            "recommended_products": recommended,
            "message": f"Found {len(matching)} item(s) in categories: {', '.join(cats)}."
        }

    except Exception as e:
        print(f"❌ [search_products] Exception: {e}")
        return {
            "products": [],
            "recommended_products": [],
            "message": f"Error searching products: {e}"
        }
