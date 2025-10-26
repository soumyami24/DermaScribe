import sqlite3
import json
import os
from contextlib import contextmanager

DB_FILE = 'products.db'
RULES_FILE = 'rules.json' # Used for sample products

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def load_rules():
    """Load the local rules engine from JSON."""
    try:
        with open(RULES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[Error] Could not load {RULES_FILE}: {e}")
        return {}

def create_tables(conn):
    """
    Create the main products table and the FTS5 virtual table for searching.
    """
    cursor = conn.cursor()
    
    # 1. Create the main products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL UNIQUE,
        brand TEXT,
        category TEXT,
        ingredients_list TEXT NOT NULL
    )
    """)
    print("✅ 'products' table created successfully.")

    # 2. Create the FTS5 virtual table
    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS products_fts USING fts5(
        product_name,
        brand,
        category,
        content='products',
        content_rowid='id'
    )
    """)
    print("✅ 'products_fts' search index created successfully.")

    # ------------------------------------------------------------------
    # --- Smart, normalizing triggers (to match app.py) ---
    # ------------------------------------------------------------------
    
    def get_cleaned_sql(column_name):
        """
        Generates a nested SQL REPLACE function for all normalization rules.
        This MUST mirror the logic in app.py's clean_search_query.
        """
        sql = f"LOWER({column_name})"
        
        # 1. Simple text replacements (must happen first)
        sql = f"REPLACE({sql}, '&', 'and')"
        sql = f"REPLACE({sql}, '''s', '')" # 's -> ''
        sql = f"REPLACE({sql}, '.', '')"   # . -> ''
        sql = f"REPLACE({sql}, '-', '')"   # - -> ''
        sql = f"REPLACE({sql}, '''', '')"  # ' -> ''

        # 2. Word concatenation replacements (must happen after)
        # This mirrors the logic in app.py's clean_search_query
        concat_replacements = [
            ('mama earth', 'mamaearth'),
            ('derma co', 'dermaco'),
            ('derma company', 'dermaco'),
            ('forest essentials', 'forestessentials')
        ]
        
        for old, new in concat_replacements:
            # These are safe as they don't contain quotes
            sql = f"REPLACE({sql}, '{old}', '{new}')"
            
        return sql

    # 3. Create triggers to keep the FTS table in sync
    
    # After INSERTS on 'products'
    cursor.execute(f"""
    CREATE TRIGGER IF NOT EXISTS products_ai
        AFTER INSERT ON products
    BEGIN
        INSERT INTO products_fts(rowid, product_name, brand, category)
        VALUES (
            new.id, 
            {get_cleaned_sql('new.product_name')},
            {get_cleaned_sql('new.brand')},
            LOWER(new.category)
        );
    END;
    """)
    
    # After DELETES on 'products'
    cursor.execute(f"""
    CREATE TRIGGER IF NOT EXISTS products_ad
        AFTER DELETE ON products
    BEGIN
        INSERT INTO products_fts(products_fts, rowid, product_name, brand, category)
        VALUES (
            'delete', 
            old.id, 
            {get_cleaned_sql('old.product_name')},
            {get_cleaned_sql('old.brand')},
            LOWER(old.category)
        );
    END;
    """)

    # After UPDATES on 'products'
    cursor.execute(f"""
    CREATE TRIGGER IF NOT EXISTS products_au
        AFTER UPDATE ON products
    BEGIN
        INSERT INTO products_fts(products_fts, rowid, product_name, brand, category)
        VALUES (
            'delete', 
            old.id, 
            {get_cleaned_sql('old.product_name')},
            {get_cleaned_sql('old.brand')},
            LOWER(old.category)
        );
        
        INSERT INTO products_fts(rowid, product_name, brand, category)
        VALUES (
            new.id, 
            {get_cleaned_sql('new.product_name')},
            {get_cleaned_sql('new.brand')},
            LOWER(new.category)
        );
    END;
    """)
    
    print("✅ Smart database triggers created successfully.")
    conn.commit()

def populate_initial_data(conn):
    """
    Populate the database with some sample products.
    The FTS triggers will handle indexing these automatically.
    """
    cursor = conn.cursor()
    
    rules = load_rules()
    sample_products = rules.get("sample_products", [])
    
    # Add your specific examples to the sample data
    sample_products.extend([
        {
            "name": "Pond's Bright Beauty De-Tan Facewash",
            "brand": "Pond's",
            "category": "cleanser",
            "ingredients": ["Myristic Acid", "Glycerin", "Water", "Niacinamide"]
        },
        {
            "name": "Dot & Key CICA Calming Blemish Clearing Facewash",
            "brand": "Dot & Key",
            "category": "cleanser",
            "ingredients": ["Aqua", "CICA", "Salicylic Acid"]
        },
        {
            "name": "Dr. Sheth's Ceramide & Vitamin C Sunscreen",
            "brand": "Dr. Sheth's",
            "category": "sunscreen",
            "ingredients": ["Aqua", "Ceramide", "Vitamin C"]
        },
        {
            "name": "The Derma Co. 1% Hyaluronic Sunscreen Aqua Gel",
            "brand": "The Derma Co.",
            "category": "sunscreen",
            "ingredients": ["Aqua", "Hyaluronic Acid", "Vitamin E"]
        },
        {
            "name": "Mamaearth Ubtan Face Wash",
            "brand": "Mamaearth",
            "category": "cleanser",
            "ingredients": ["Aqua", "Turmeric", "Saffron"]
        },
        {
            "name": "Paula's Choice 2% BHA Liquid Exfoliant",
            "brand": "Paula's Choice",
            "category": "treatment",
            "ingredients": ["Water", "Methylpropanediol", "Butylene Glycol", "Salicylic Acid"]
        }
    ])
    
    print(f"ℹ️ Attempting to add {len(sample_products)} sample products...")
    
    products_added = 0
    for product in sample_products:
        try:
            cursor.execute(
                "INSERT INTO products (product_name, brand, category, ingredients_list) VALUES (?, ?, ?, ?)",
                (
                    product['name'], 
                    product.get('brand', 'N/A'), 
                    product.get('category', 'N/A'), 
                    json.dumps(product.get('ingredients', []))
                )
            )
            products_added += 1
        except sqlite3.IntegrityError:
            # This product_name already exists, skip it.
            pass
        except Exception as e:
            print(f"[Error] Failed to insert product {product.get('name')}: {e}")

    conn.commit()
    print(f"✅ Added {products_added} new sample products to the database.")

def main():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"🗑️ Removed old {DB_FILE}.")
        
    print(f"🚀 Building new database: {DB_FILE}...")
    
    with get_db_connection() as conn:
        create_tables(conn)
        populate_initial_data(conn)
        
    print("🎉 Database build complete!")

if __name__ == "__main__":
    main()