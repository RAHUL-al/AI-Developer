import os
import sys
from demo_data import DEMO_PRODUCTS
from models import Product

def main():
    # Handle --force flag to reinitialize
    if "--force" in sys.argv:
        print("Force reinitializing database...")
        for f in ["products.index", "products.json"]:
            if os.path.exists(f):
                os.remove(f)
                print(f"  Deleted {f}")
    
    # Import after potential deletion to get fresh state
    from vector_store import get_vector_store
    
    store = get_vector_store()
    
    if not store.is_empty():
        print(f"\n{'='*50}")
        print(f"  Database already initialized!")
        print(f"  Products in store: {len(store.products)}")
        print(f"{'='*50}")
        print(f"\n  Use --force to reinitialize with fresh data.")
        print(f"  Example: python init_data.py --force")
        print(f"\n  To start the server, run: python app.py\n")
        return
    
    # Initialize with demo products
    print(f"\n{'='*50}")
    print(f"  Initializing Smart Search Database")
    print(f"{'='*50}\n")
    
    products = [Product(**p) for p in DEMO_PRODUCTS]
    print(f"Loading {len(products)} demo products...\n")
    
    store.add_products(products)
    store.save()
    
    print(f"\n{'='*50}")
    print(f"  [OK] Initialization Complete!")
    print(f"  Products stored: {len(store.products)}")
    print(f"{'='*50}")
    print(f"\n  To start the server, run: python app.py\n")

if __name__ == "__main__":
    main()
