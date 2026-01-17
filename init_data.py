import os, sys
from demo_data import DEMO_PRODUCTS
from models import Product

if "--force" in sys.argv:
    for f in ["products.index", "products.json"]:
        if os.path.exists(f): os.remove(f); print(f"Deleted {f}")

from vector_store import get_vector_store

def main():
    store = get_vector_store()
    if not store.is_empty():
        print(f"Already have {len(store.products)} products. Use --force to reinit.")
        return
    products = [Product(**p) for p in DEMO_PRODUCTS]
    print(f"Adding {len(products)} products...")
    store.add_products(products)
    store.save()
    print("Done! Run: python app.py")

if __name__ == "__main__":
    main()
