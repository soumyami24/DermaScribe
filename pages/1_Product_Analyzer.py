import streamlit as st
import sqlite3
import json
import os
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime
from contextlib import contextmanager
from typing import List, Dict, Optional

# Attempt to import AI handler, fail gracefully if not present
try:
    from pages.ai_handler import find_new_product_with_ai, get_deep_analysis_from_ai, is_ai_configured
except ImportError:
    
    # Define placeholder functions and use st.error/st_themed_callout where needed
    def is_ai_configured(): 
        st_themed_callout("❌ Missing `ai_handler.py`. AI features will be disabled.", level="error")
        return False

    def find_new_product_with_ai(query): return {"error": "ai_handler.py not found."}
    def get_deep_analysis_from_ai(products): return {"error": "ai_handler.py not found."}


# Page configuration
st.set_page_config(
    page_title="DermacScribe AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM THEMED CALLOUT FUNCTION (Replaces st.info/warning/error for messages) ---
def st_themed_callout(message: str, level: str = "info"):
    """Renders a custom, themed callout box using the light purple/info style."""
    
    icon_map = {
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌",
        "success": "✅"
    }
    
    # Define colors based on existing CSS variables for Aurora Glow theme
    border_color_map = {
        "info": "var(--color-accent-purple)",
        "warning": "var(--color-gradient-start)",
        "error": "var(--color-error-border)", 
        "success": "var(--color-success-border)"
    }
    
    text_color_map = {
        "info": "var(--color-text-dark)",
        "warning": "var(--color-text-dark)",
        "error": "var(--color-error-text)", 
        "success": "var(--color-text-dark)"
    }
    
    st.markdown(
        f"""
        <div class="callout-container" style="border-left: 5px solid {border_color_map[level]};">
            <p style="color: {text_color_map[level]};">
                {icon_map[level]} <b>{message}</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# --- NEW STYLING (Theming and Aurora Glow CSS) ---
st.markdown("""
<style>
    /* Import Google Fonts - Lora (Headings) and Montserrat (Body) */
    @import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;600;700&family=Montserrat:wght@300;400;500;600&display=swap');

    /* "Aurora Glow" Palette */
    :root {
        --color-bg-light: #FDFBFF;       /* Soft Off-White */
        --color-bg-card: #FFFFFF;        /* White */
        --color-text-dark: #4A3F5E;     /* Dark Purple/Gray */
        --color-text-medium: #6D617A;    /* Medium Purple/Gray */
        --color-accent-purple: #957DAD; /* Elegant Purple */
        --color-gradient-start: #FFD1DC; /* Soft Pink */
        --color-gradient-end: #E0BBE4;     /* Soft Lavender */
        --color-border: #EAE6F0;         /* Light Purple/Gray Border */
        
        /* Retaining colors for internal use in the custom callout function */
        --color-error-text: #8A303F;
        --color-error-border: #FFD1DC;
        --color-success-border: var(--color-accent-purple);
        --color-info-bg: #F6F4FF; /* Light purple bg for custom callout */


        --font-heading: 'Lora', serif;
        --font-body: 'Montserrat', sans-serif;
        
        /* --- THIS SECTION FIXES THE BUTTONS (Primary is Light Pink/Lavender Gradient) --- */
        --gradient-main: linear-gradient(135deg, var(--color-gradient-start) 0%, var(--color-gradient-end) 100%);
    }

    /* --- Global Styles --- */
    html, body, .stApp { 
        font-family: var(--font-body); 
        color: var(--color-text-medium); 
        background-color: var(--color-bg-light); 
    }
    .main .block-container { 
        padding: 2rem 3rem; 
    }
    header, footer { 
        visibility: hidden; 
        height: 0px !important; 
    }
    h1, h2, h3, h4, h5, h6 { 
        font-family: var(--font-heading); 
        color: var(--color-text-dark); 
        font-weight: 600; 
    }
    h1 { font-size: 3.5rem; text-align: center; } 
    h2 { font-size: 2.5rem; margin-bottom: 2rem; text-align: center;} 
    h3 { font-size: 1.8rem; text-align: left; } /* Subheaders are left-aligned */
    
    p, li {
        font-size: 1.1rem;
        color: var(--color-text-medium);
    }
    
    /* Center-aligned paragraphs */
    p.center {
        text-align: center;
    }

    /* --- Base Card --- */
    .card-container { 
        background-color: var(--color-bg-card); 
        border-radius: 20px; 
        padding: 2.5rem; 
        border: 1px solid var(--color-border); 
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05); 
    }

    /* --- Base Button Styles (for all buttons) --- */
    .stButton > button {
        font-family: var(--font-body); 
        font-weight: 600; 
        padding: 0.8rem 1rem;
        border-radius: 30px; 
        border: none; 
        transition: all 0.3s ease; 
        text-transform: uppercase; 
        letter-spacing: 0.5px;
    }
    
    /* --- Primary Buttons (Gradients - Light Pink/Lavender - Replaces Red) --- */
    .stButton > button:not([kind="secondary"]) {
        background: var(--gradient-main); 
        color: var(--color-text-dark); 
        box-shadow: 0 4px 15px rgba(149, 125, 173, 0.3);
    }
    .stButton > button:not([kind="secondary"]):hover { 
        transform: translateY(-3px); 
        box-shadow: 0 6px 20px rgba(149, 125, 173, 0.4); 
    }
    .stButton > button:not([kind="secondary"]):disabled { 
        background: var(--color-border) !important; 
        color: var(--color-text-medium) !important; 
        box-shadow: none !important; 
        cursor: not-allowed !important;
    }

    /* --- Secondary Buttons (Outlines - Purple) --- */
    .stButton > button[kind="secondary"] {
        background-color: transparent; 
        color: var(--color-accent-purple); 
        border: 2px solid var(--color-accent-purple); 
        box-shadow: none;
    }
    .stButton > button[kind="secondary"]:hover { 
        background-color: var(--color-accent-purple); 
        color: var(--color-bg-card); 
        transform: translateY(-2px); 
    }
    .stButton > button[kind="secondary"]:disabled {
        background-color: var(--color-bg-light);
        border-color: var(--color-border);
        color: var(--color-text-medium);
        transform: none;
        box-shadow: none;
        cursor: not-allowed;
    }
    
    /* --- Style Download Button like Secondary --- */
    .stDownloadButton > button {
        font-family: var(--font-body); 
        font-weight: 600; 
        padding: 0.8rem 1rem;
        border-radius: 30px; 
        transition: all 0.3s ease; 
        text-transform: uppercase; 
        letter-spacing: 0.5px;
        background-color: transparent; 
        color: var(--color-accent-purple); 
        border: 2px solid var(--color-accent-purple); 
        box-shadow: none;
        width: 100%;
    }
    .stDownloadButton > button:hover { 
        background-color: var(--color-accent-purple); 
        color: var(--color-bg-card); 
        transform: translateY(-2px); 
    }
    
    /* --- Styles for Product/Analysis Cards --- */
    .product-card {
        padding: 1rem;
        margin: 5px 0;
        border-left: 5px solid var(--color-accent-purple);
        background-color: var(--color-bg-light);
        border-radius: 8px;
        border: 1px solid var(--color-border);
    }
    .analysis-section {
        background-color: var(--color-bg-card);
        padding: 2rem;
        margin: 10px 0;
        border-radius: 16px;
        border: 1px solid var(--color-border);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
    }
    
    /* --- Custom Purple Callout Container (Target of st_themed_callout) --- */
    .callout-container {
        background-color: var(--color-info-bg); /* Light purple */
        border-left: 5px solid var(--color-accent-purple);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid var(--color-border);
        border-left-width: 5px; 
    }
    .callout-container p {
        font-family: var(--font-body);
        font-weight: 500;
        font-size: 1.1rem;
        color: var(--color-text-dark);
        margin: 0;
    }
    /* --- Circular Progress Rating --- */
    .circular-progress {
        position: relative;
        width: 100px; 
        height: 100px;
        border-radius: 50%;
        display: grid;
        place-items: center;
        background: conic-gradient(var(--progress-color) calc(var(--progress-value) * 3.6deg), var(--color-border) 0deg);
        margin-left: 10px; 
    }
    .circular-progress::before {
        content: "";
        position: absolute;
        width: 80px; 
        height: 80px;
        background: var(--color-bg-card); 
        border-radius: 50%;
    }
    .progress-value {
        position: relative;
        font-size: 1.5rem;
        font-weight: bold;
        color: var(--progress-color);
        font-family: var(--font-body);
    }
</style>
""", unsafe_allow_html=True)
# --- END NEW CSS ---


# --- Configuration & Constants ---
DB_FILE = 'products.db'
RULES_FILE = os.path.join(os.path.dirname(__file__), 'rules1.json')
APP_VERSION = "1.1.0"

# --- Database Utilities ---
@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def db_check() -> bool:
    """Check if database exists and is valid."""
    if not os.path.exists(DB_FILE):
        return False
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
            return cursor.fetchone() is not None
    except Exception as e:
        st_themed_callout(f"Database check failed: {e}", level="error") 
        return False

# --- Cache Resources ---
@st.cache_resource
def load_rules():
    """Load the local rules engine from JSON."""
    try:
        with open(RULES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st_themed_callout(f"Error loading rules ({RULES_FILE}): {e}", level="error")
        return {}

RULES = load_rules()

# --- Session State Management ---
def initialize_session_state():
    """Initialize all session state variables."""
    defaults = {
        "routine_products": [],
        "show_deep_analysis_button": False,
        "last_analysis": None,
        "analysis_history": [],
        "app_initialized": True,
        "search_results_options": None, 
        "current_search_query": None    
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# --- Product Search Logic ---
@st.cache_data(ttl=3600) 
def search_local_db(query: str) -> List[Dict]:
    """Uses FTS5 for fast, normalized search & returns a LIST of top matches (up to 5)."""
    def clean_search_query(q: str) -> str:
        q = q.strip().lower()
        replacements = [('&', 'and'), ("'s", ''), ('.', ''), ('-', ''), ("'", ''), ('%', '')]
        for old, new in replacements: q = q.replace(old, new)
        concat_replacements = [('mama earth', 'mamaearth'), ('derma co', 'dermaco'),
                                 ('derma company', 'dermaco'), ('forest essentials', 'forestessentials')]
        for old, new in concat_replacements: q = q.replace(old, new)
        return q
    # ----------------------------------------------------
    if not query or not query.strip(): return []
    search_query = clean_search_query(query)
    search_terms = [f'{term.strip()}*' for term in search_query.split() if term.strip()]
    if not search_terms: return []
    fts_query = " ".join(search_terms)
    results_list = []
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            sql_query = """
            SELECT
                p.product_name, p.brand, p.category, p.ingredients_list, fts.rank
            FROM products p, products_fts fts
            WHERE p.id = fts.rowid AND fts.products_fts MATCH ?
            ORDER BY fts.rank LIMIT 5;
            """
            cursor.execute(sql_query, (fts_query,))
            results = cursor.fetchall()
            for row in results:
                match = dict(row)
                try: ingredients = json.loads(match['ingredients_list'])
                except json.JSONDecodeError: ingredients = []
                standardized_product = {
                    'name': match['product_name'], 'brand': match['brand'],
                    'category': match['category'], 'ingredients': ingredients
                }
                results_list.append(standardized_product)
    except Exception as e:
        st_themed_callout(f"Database search error: {e}", level="error")
        print(f"[Error] FTS5 query failed. Query: {fts_query}, Error: {e}")
    return results_list

# --- Add Product to DB ---
def add_product_to_db(product_data: Dict) -> bool:
    """Saves a new product (from AI) to the database. Returns True if added."""
    if not product_data.get('name') or not isinstance(product_data.get('ingredients'), list):
        st_themed_callout("Invalid product data received from AI.", level="error")
        return False
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            ingredients_json = json.dumps(product_data['ingredients'])
            cursor.execute(
                "INSERT INTO products (product_name, brand, category, ingredients_list) VALUES (?, ?, ?, ?)",
                (product_data['name'], product_data.get('brand', 'N/A'),
                product_data.get('category', 'N/A'), ingredients_json)
            )
            conn.commit()
            search_local_db.clear()
            return True
    except sqlite3.IntegrityError:
        st_themed_callout(f"Product '{product_data['name']}' already exists in database.", level="warning")
        return False
    except Exception as e:
        st_themed_callout(f"Failed to save product to database: {e}", level="error")
        return False

# --- Standard Analysis Logic ---
def run_standard_analysis(products: List[Dict]) -> Dict:
    """Runs the free, local analysis using rules.json."""
    found_actives, product_map, category_issues, warnings, pairings = [], {}, [], [], []
    ingredient_profiles = RULES.get('ingredient_profiles', {})
    for product in products:
        product_actives = []
        prod_name = product.get('name', 'Unknown Product')
        ingredients_lower = [str(ing).lower() for ing in product.get('ingredients', [])]
        for keyword, ing_key in RULES.get('keywords_to_ingredients', {}).items():
            if any(keyword in ing for ing in ingredients_lower):
                if ing_key not in product_actives: product_actives.append(ing_key)
        if product_actives:
            found_actives.extend(product_actives)
            for active in product_actives:
                if active not in product_map: product_map[active] = []
                product_map[active].append(prod_name)
    found_actives = list(set(found_actives))
    for active1 in found_actives:
        profile1 = ingredient_profiles.get(active1)
        if not profile1: continue
        name1 = profile1.get('display_name', active1)
        prods1 = ", ".join([f"*{p}*" for p in product_map.get(active1, [])])
        for active2 in found_actives:
            if active1 == active2: continue
            profile2 = ingredient_profiles.get(active2);
            if not profile2: continue
            name2 = profile2.get('display_name', active2)
            prods2 = ", ".join([f"*{p}*" for p in product_map.get(active2, [])])
            if active2 in profile1.get('conflicts_with', []):
                w = f"❌ **Conflict:** '{name1}' (in {prods1}) conflicts with '{name2}' (in {prods2})."
                rw = f"❌ **Conflict:** '{name2}' (in {prods2}) conflicts with '{name1}' (in {prods1})."
                if w not in warnings and rw not in warnings: warnings.append(w)
            if active2 in profile1.get('pairs_well_with', []):
                p = f"✅ **Synergy:** '{name1}' (in {prods1}) pairs well with '{name2}' (in {prods2})."
                rp = f"✅ **Synergy:** '{name2}' (in {prods2}) pairs well with '{name1}' (in {prods1})."
                if p not in pairings and rp not in pairings: pairings.append(p)
    categories = [p.get('category', 'unknown').lower() for p in products]
    category_rules = RULES.get('category_rules', {})
    essential_cats = [cat.lower() for cat, rules in category_rules.items() if rules.get('essential')]
    missing = [cat for cat in essential_cats if cat not in categories]
    if missing: category_issues.append(f"⚠️ **Missing essentials:** {', '.join(missing).title()}")
    am_routine, pm_routine = generate_optimized_routine(products, found_actives)
    
    # --- Convert to AI-like format for consistent display ---
    rating = 5
    if warnings: rating -= 2
    if category_issues: rating -= 1
    rating = max(1, rating) # Ensure rating is at least 1
    
    summary = "Your routine has some potential conflicts or gaps."
    if rating == 5: summary = "Your routine looks solid based on local rules!"
    elif rating == 4: summary = "Your routine is good, but check the minor gaps."
        
    return {
        "rating": rating,
        "summary": summary,
        "conflicts": warnings or ["No specific ingredient conflicts were identified."],
        "warnings": ["Standard analysis does not provide critical usage warnings. Use PRO AI for this."],
        "gap_analysis": (category_issues or ["Routine appears complete regarding essential steps."])[0],
        "recommendations": pairings or ["No specific recommendations identified by rules."],
        "routine": {"am": am_routine, "pm": pm_routine},
        "active_ingredients": [ingredient_profiles.get(act, {}).get('display_name', act) for act in found_actives],
        "timestamp": datetime.now().isoformat(),
        "analysis_type": "standard" # Add a flag
    }


def generate_optimized_routine(products: List[Dict], active_ingredients: List[str]) -> tuple:
    """Generate optimized AM/PM routine."""
    category_rules = RULES.get('category_rules', {})
    am_steps, pm_steps = [], []
    product_ingredients_map = {p.get('name'): [str(ing).lower() for ing in p.get('ingredients', [])] for p in products}
    for product in products:
        category = product.get('category', 'serum').lower()
        rules = category_rules.get(category, {"step": 5, "time": "AM/PM"})
        time_rule = rules.get('time', 'AM/PM')
        step = rules.get('step', 5)
        product_name = product.get('name', 'Unknown Product')
        ingredients_lower = product_ingredients_map.get(product_name, [])
        product_has_retinol = any('retinol' in ing for ing in ingredients_lower)
        product_has_vitc = any('ascorbic' in ing for ing in ingredients_lower)
        final_time = time_rule
        if product_has_retinol: final_time = 'PM'
        elif category == 'sunscreen': final_time = 'AM'; step = 10
        elif product_has_vitc and time_rule != 'PM': final_time = 'AM'
        entry = (step, product_name)
        if 'AM' in final_time: am_steps.append(entry)
        if 'PM' in final_time: pm_steps.append(entry)
    am_steps.sort(key=lambda x: x[0]); pm_steps.sort(key=lambda x: x[0])
    am_routine = " → ".join([name for _, name in am_steps]) if am_steps else "No products suggested for AM."
    pm_routine = " → ".join([name for _, name in pm_steps]) if pm_steps else "No products suggested for PM."
    return am_routine, pm_routine

# --- Product Management ---
def remove_product(index: int):
    """Remove product from routine list using index."""
    if 0 <= index < len(st.session_state.routine_products):
        removed = st.session_state.routine_products.pop(index)
        st.success(f"Removed: **{removed.get('name', 'Unknown Product')}**")
        st.session_state.last_analysis = None
    else:
        st_themed_callout("Failed to remove product: Invalid index.", level="error")

def clear_routine():
    """Clear entire routine and related state."""
    st.session_state.routine_products = []
    st.session_state.last_analysis = None
    clear_search_options()
    st.success("Routine cleared.")

def export_routine() -> str:
    """Export current routine and last analysis as JSON string."""
    export_data = {
        "metadata": {"app": "DermacScribe AI", "version": APP_VERSION, "exported_at": datetime.now().isoformat(), "product_count": len(st.session_state.routine_products)},
        "products": st.session_state.routine_products,
        "last_analysis": st.session_state.last_analysis
    }
    try: return json.dumps(export_data, indent=2)
    except Exception as e: 
        st_themed_callout(f"Export failed: {e}", level="error"); return "{}"

# --- Search Ambiguity Handling Helpers ---
def trigger_ai_search(query: str):
    """Handles the AI search process when called via button click."""
    clear_search_options()
    st_themed_callout(f"Searching with AI for '{query}'...", level="info")
    progress_bar = st.progress(0, text="Initializing AI...")
    status_text = st.empty()
    product_data = None
    try:
        stages = ["🔍 Initializing...", "🌐 Querying...", "📊 Parsing...", "✅ Finalizing..."]
        num_stages = len(stages)
        for i, stage in enumerate(stages):
            progress = int(((i + 1) / num_stages) * 100)
            progress_bar.progress(progress, text=stage)
            status_text.text(stage)
            if i < num_stages - 1: time.sleep(0.5)
            
        product_data = find_new_product_with_ai(query) # ASSUMES THIS FUNCTION EXISTS
        
        progress_bar.progress(100, text="AI Search Complete.")
        status_text.empty()
        if product_data and "error" not in product_data:
            product_name = product_data.get('name', 'Unknown Product')
            if any(p.get('name') == product_name for p in st.session_state.routine_products):
                st_themed_callout(f"'{product_name}' is already in your routine.", level="warning")
            else:
                st.success(f"✅ AI found: **{product_name}**")
                st.session_state.routine_products.append(product_data)
        else:
            error_msg = product_data.get('error', 'AI: No match found') if product_data else 'AI search failed'
            st_themed_callout(f"AI couldn't find '{query}'. Error: {error_msg}", level="error")
            st_themed_callout("Try a more specific query.", level="info")
    except Exception as e:
        st_themed_callout(f"AI search error: {e}", level="error")
        st_themed_callout("Check API status or try again.", level="info")
    finally:
        progress_bar.empty(); status_text.empty()

def clear_search_options():
    """Clears search options from session state."""
    if "search_results_options" in st.session_state:
        st.session_state.search_results_options = None
    if "current_search_query" in st.session_state:
        st.session_state.current_search_query = None

def add_selected_product(selected_product_index: int):
    """Adds the selected product (using index) to routine via button click."""
    options = st.session_state.get("search_results_options")
    if options and 0 <= selected_product_index < len(options):
        product_to_add = options[selected_product_index]
        product_name = product_to_add.get('name')
        if any(p.get('name') == product_name for p in st.session_state.routine_products):
            st_themed_callout(f"'{product_name}' is already in routine.", level="warning")
        else:
            st.session_state.routine_products.append(product_to_add)
            st.success(f"✅ Added: **{product_name}**")
        clear_search_options()
    else:
        st_themed_callout("Invalid selection.", level="error")
        clear_search_options()

# --- Search UI Rendering ---
def render_search_ui():
    """Renders search input form OR selection UI based on state."""
    st.markdown("<h2>🔍 Add Products</h2>", unsafe_allow_html=True)
    if st.session_state.get("search_results_options"):
        render_product_selection()
    else:
        render_search_form()

def render_search_form():
    """Renders the search input form."""
    with st.form(key="product_form", clear_on_submit=True):
        product_query = st.text_input("Search for product", placeholder="e.g., Mamaearth Ubtan , POND’S Super Light Gel...",
                                     help="Enter brand + name. Handles typos.", key="product_query_input")
        # Primary button uses the light pink/lavender gradient
        submit_button = st.form_submit_button("🔎 Search & Add", use_container_width=True, type="primary")

    if submit_button and product_query:
        clear_search_options() 
        handle_product_search(product_query) 

def render_product_selection():
    """Renders UI for selecting from multiple local matches."""
    options = st.session_state.search_results_options
    query = st.session_state.current_search_query
    st_themed_callout(f"Multiple local matches for **'{query}'**. Select one or search online:", level="info")
    
    option_names = [f"{p.get('name', '?')} ({p.get('brand', 'N/A')})" for p in options]
    selected_name = st.radio("Select correct product:", option_names, index=0,
                             key="product_selection_radio")
    
    selected_idx = option_names.index(selected_name)
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1: 
        st.button("✅ Add Selected", use_container_width=True, type="primary",
                  on_click=add_selected_product, args=(selected_idx,))
    with col2: 
        st.button("🤖 Search Online (AI)", use_container_width=True, type="secondary",
                  on_click=trigger_ai_search, args=(query,))
    with col3: 
        st.button("❌ Cancel", use_container_width=True, type="secondary",
                  on_click=clear_search_options)

# --- Search Handling Logic ---
def handle_product_search(query: str):
    """Handles product search: local first, then AI or selection UI."""
    if not query or not query.strip():
        st_themed_callout("Please enter a product name.", level="error"); return
    with st.spinner(f"Searching local DB for '{query}'..."):
        local_results = search_local_db(query)
    if not local_results: 
        if not is_ai_configured():
            st_themed_callout(f"'{query}' not in local DB. AI search is not configured.", level="error")
        else:
            trigger_ai_search(query)
    elif len(local_results) == 1:
        product = local_results[0]
        if any(p.get('name') == product.get('name') for p in st.session_state.routine_products):
            st_themed_callout(f"'{product.get('name')}' is already in routine.", level="warning")
        else:
            st.success(f"✅ Found in local DB: **{product.get('name')}**")
            st.session_state.routine_products.append(product)
            st.rerun()
    else: 
        st.session_state.search_results_options = local_results
        st.session_state.current_search_query = query
        st.rerun() # Rerun to show selection UI

# --- Routine Display ---
def render_current_routine():
    """Render current routine display."""
    if not st.session_state.routine_products:
        st.caption("Routine is empty. Use search to add products.")
        return
        
    st.markdown("<h2>📋 Your Current Routine</h2>", unsafe_allow_html=True)
    
    for i, product in enumerate(st.session_state.routine_products):
        col1, col2 = st.columns([3, 1])
        with col1: 
            st.markdown(f'<div class="product-card"><b>{product.get("name", "?")}</b><br><small>Brand: {product.get("brand", "?")} | Cat: {product.get("category", "?")}</small></div>', unsafe_allow_html=True)
        with col2:
            st.button("Remove", key=f"remove_{i}", help="Remove this product", 
                      on_click=remove_product, args=(i,), 
                      type="secondary", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: 
        st.button("🔄 Clear Routine", use_container_width=True, 
                  on_click=clear_routine, type="secondary")
    with col2:
        st.download_button(label="📥 Export Routine", data=export_routine(),
                            file_name=f"dermacscribe_{datetime.now():%Y%m%d_%H%M}.json",
                            mime="application/json", use_container_width=True, key="export_btn")

# --- Analysis Section ---
def render_analysis_section():
    """Render analysis buttons and results area."""
    
    if len(st.session_state.routine_products) < 2:
        st.markdown("---")
        # Custom callout container used here
        st.markdown(
            '<div class="callout-container"><p>ℹ️ Add at least 2 products to your routine to enable analysis.</p></div>', 
            unsafe_allow_html=True
        )
        if st.session_state.last_analysis: st.session_state.last_analysis = None
        return
        
    st.markdown("---")
    st.markdown("<h2>🔬 Analyze Routine</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p class='center'>Choose your analysis method. The PRO AI analysis provides a deeper, customized report.</p>", 
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns(2)
    with col1: 
        # Secondary style (purple outline)
        st.button("🧪 Run Standard Analysis", type="secondary", use_container_width=True, 
                  on_click=perform_standard_analysis, key="std_analysis_btn_v2",
                  help="Fast, local analysis based on pre-defined rules.")
    with col2:
        ai_ok = is_ai_configured()
        label = "✨ Run PRO AI Analysis" if ai_ok else "✨ PRO AI Analysis (Needs API Key)"
        help_txt = "Get a deep, professional AI-powered analysis (up to 45s)" if ai_ok else "Configure Gemini API key to unlock"
        # Primary style (light pink/lavender gradient)
        st.button(label, use_container_width=True, disabled=not ai_ok, help=help_txt, 
                  on_click=perform_deep_analysis, key="deep_analysis_btn_v2", 
                  type="primary") 
    
    if st.session_state.get("last_analysis"): 
        display_analysis_results()

def perform_standard_analysis():
    """Perform standard analysis, update state via button click."""
    if len(st.session_state.routine_products) < 2: st.toast("Need >= 2 products.", icon="⚠️"); return
    with st.spinner("Running local analysis..."):
        results = run_standard_analysis(st.session_state.routine_products)
        st.session_state.last_analysis = results
        st.session_state.analysis_history.append({
            "type": "standard", 
            "ts": datetime.now().isoformat(),
            "count": len(st.session_state.routine_products),
            "rating": results.get("rating")
        })
    st.toast("Standard analysis complete!", icon="🧪")

def perform_deep_analysis():
    """Perform CONCISE deep AI analysis, update state via button click."""
    if len(st.session_state.routine_products) < 2: st.toast("Need >= 2 products.", icon="⚠️"); return
    if not is_ai_configured(): 
        st_themed_callout("AI not configured.", level="error"); return
    
    progress_bar = st.progress(0, text="Initializing AI...")
    status_text = st.empty()
    results = None
    try:
        stages = ["🧠 Initializing...", "🔬 Analyzing...", "💡 Checking...", "✅ Generating..."]
        num_stages = len(stages)
        for i, stage in enumerate(stages):
            progress = int(((i + 1) / num_stages) * 100)
            progress_bar.progress(progress, text=stage)
            status_text.text(stage)
            if i < num_stages - 1: time.sleep(0.8)
            
        results = get_deep_analysis_from_ai(st.session_state.routine_products)
        
        progress_bar.progress(100, text="AI Analysis Complete!")
        status_text.empty()
        if results and "error" not in results:
            results["analysis_type"] = "deep_ai"
            st.session_state.last_analysis = results
            st.session_state.analysis_history.append({"type": "deep_ai_concise", "ts": datetime.now().isoformat(), "count": len(st.session_state.routine_products), "rating": results.get('rating')})
            st.success("🎉 Concise AI analysis complete!")
        else:
            err = results.get('error', "Unknown AI error") if results else "No AI response"
            st_themed_callout(f"AI Analysis Failed: {err}", level="error")
            st_themed_callout("Try fewer products?", level="info")
            st.session_state.last_analysis = None
    except Exception as e:
        st_themed_callout(f"Analysis error: {e}", level="error")
        st_themed_callout("Try fewer products?", level="info")
        st.session_state.last_analysis = None
    finally:
        progress_bar.empty(); status_text.empty()

# --- Analysis Display Helper ---
def _display_list_items(items: Optional[List[str]], prefix: str = "•", default_msg: str = "N/A", level: str = "info"):
    """Helper to display list items safely with styling."""
    
    concise_defaults = ["No critical conflicts detected.", "No major gaps identified.", "None",
                         "No specific actions recommended by AI.", "No major conflicts identified by AI.",
                         "No specific ongoing tips provided.", "No specific recommendations provided.",
                         "Your routine appears complete regarding essential steps.",
                         "No critical usage warnings identified."
                         ]
    is_default = not items or not isinstance(items, list) or (len(items) == 1 and items[0] in concise_defaults)
    is_std_default_conflict = (len(items) == 1 and items[0] == "No specific ingredient conflicts were identified.")
    
    if not is_default:
        for item in items:
            if item and isinstance(item, str) and item.strip():
                st.markdown(f"{prefix} {item.strip()}")
    
    elif is_std_default_conflict:
        st.markdown(f'<p style="color:var(--color-text-dark);">✅ Great news! <b>No specific ingredient conflicts were identified.</b></p>', unsafe_allow_html=True)
        analysis_type = st.session_state.last_analysis.get("analysis_type", "deep_ai")
        if analysis_type == "standard":
             st.caption("This is based on the local rules engine. For a deeper check, use the PRO AI analysis.")
        else:
             st.caption("This is based on the AI's analysis of the primary active ingredients in your products against known negative interactions.")
    
    else:
        st.caption(f"_{default_msg}_")

# --- Analysis Display Function ---
def display_analysis_results():
    """Display CONCISE analysis results focusing on key takeaways."""
    results = st.session_state.last_analysis
    if not results: return
    
    analysis_type = results.get("analysis_type", "deep_ai")
    title_text = "📊 Key AI Analysis Insights" if analysis_type == "deep_ai" else "📊 Key Standard Analysis Insights"

    # Use the themed analysis section container
    st.markdown('<hr><div class="analysis-section" style="border-top: 5px solid var(--color-accent-purple);">', unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; font-size: 2.2rem;'>{title_text}</h3>", unsafe_allow_html=True)

    # --- Rating & Summary ---
    rating = results.get('rating', 3)
    percentage = rating * 20 
    summary = results.get('summary', 'Analysis summary unavailable.')
    
    color_map = {
        1: "var(--color-error-text)", 2: "var(--color-error-text)", 
        3: "#f0ad4e", # Yellow/Amber
        4: "#6A994E", 5: "#6A994E" # Green
    }
    progress_color = color_map.get(rating, "var(--color-accent-purple)")
    
    col1, col2 = st.columns([1, 3]) 
    with col1:
        st.markdown(f"""
        <div style="--progress-value:{percentage}; --progress-color:{progress_color};">
            <div class="circular-progress">
                <span class="progress-value">{percentage}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("<h3>Overall Assessment</h3>", unsafe_allow_html=True) 
        st.markdown(f"**{summary}**")
    
    st.markdown("---")

    # --- Conflicts & Warnings ---
    conflicts = results.get('conflicts', [])
    warnings = results.get('warnings', [])
    
    default_conflict_msgs = ["No specific ingredient conflicts were identified."]
    has_real_conflicts = conflicts and isinstance(conflicts, list) and (len(conflicts) > 0 and not all(c in default_conflict_msgs for c in conflicts))

    default_warning_msgs = ["No critical usage warnings identified.", "No major conflicts identified by AI.", "No critical conflicts detected.", "Standard analysis does not provide critical usage warnings. Use PRO AI for this."]
    has_real_warnings = warnings and isinstance(warnings, list) and \
                        (len(warnings) > 0 and not all(w in default_warning_msgs for w in warnings))
    
    expand_section = has_real_conflicts or has_real_warnings
    expander_title = "🚨 Critical Issues Found" if expand_section else "✅ Warnings & Conflicts"

    with st.expander(expander_title, expanded=expand_section):
        st.markdown("<h3>Specific Ingredient Conflicts</h3>", unsafe_allow_html=True)
        _display_list_items(conflicts, prefix="❌", default_msg="No specific conflicts were reported.", level="error")
        
        st.markdown("---") 
        
        st.markdown("<h3>Critical Usage Warnings</h3>", unsafe_allow_html=True)
        if has_real_warnings:
            _display_list_items(warnings, prefix="⚠️", default_msg="N/A", level="warning")
        elif analysis_type == "standard":
            st_themed_callout("Standard analysis does not check for usage warnings. Use PRO AI for this feature.", level="info")
        else:
            st_themed_callout("No critical usage warnings were flagged by the AI.", level="success")

    # --- Gap Analysis ---
    st.markdown("<h3>🎯 Routine Completeness (Gap Analysis)</h3>", unsafe_allow_html=True)
    gap_analysis_text = results.get('gap_analysis', "Could not determine routine completeness.")
    is_complete = "appears complete" in gap_analysis_text.lower() or gap_analysis_text == "None"
    
    if is_complete: 
        st.markdown(f'<p style="color:var(--color-text-dark);">✅ <b>{gap_analysis_text}</b></p>', unsafe_allow_html=True)
    else: 
        st_themed_callout(f"Routine Gap Identified: {gap_analysis_text}", level="warning")

    st.markdown("---")

    # --- Recommendations ---
    recommendations = results.get('recommendations', [])
    rec_title = "💡 Recommended Actions" if analysis_type == "deep_ai" else "✅ Identified Synergies (Pairings)"
    has_real_recs = recommendations and isinstance(recommendations, list) and (len(recommendations) > 1 or "Continue routine" not in recommendations[0])
    
    if has_real_recs or analysis_type == "standard":
        st.markdown(f"<h3>{rec_title}</h3>", unsafe_allow_html=True)
        _display_list_items(recommendations, prefix="➡️", default_msg="No specific recommendations provided.", level="info")
        st.markdown("---")

    # --- Routine Order ---
    if results.get('routine') and isinstance(results.get('routine'), dict):
        with st.expander("🕒 Suggested Routine Order", expanded=True):
            routine = results['routine']
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<h3>☀️ Morning (AM)</h3>", unsafe_allow_html=True)
                am_routine_str = routine.get('am', "")
                am_steps = am_routine_str.split(' → ') if am_routine_str and am_routine_str != "No products suggested for AM." else []
                if not am_steps or "Not specified" in am_steps: st.caption("_No AM routine suggested._")
                else:
                    for i, step in enumerate(am_steps): st.markdown(f"`{i+1}` **{step.strip()}**")
            with col2:
                st.markdown("<h3>🌙 Evening (PM)</h3>", unsafe_allow_html=True)
                pm_routine_str = routine.get('pm', "")
                pm_steps = pm_routine_str.split(' → ') if pm_routine_str and pm_routine_str != "No products suggested for PM." else []
                if not pm_steps or "Not specified" in pm_steps: st.caption("_No PM routine suggested._")
                else:
                    for i, step in enumerate(pm_steps): st.markdown(f"`{i+1}` **{step.strip()}**")

    st.markdown('</div>', unsafe_allow_html=True)

# --- History Graph Section ---
def render_history_graph():
    """Renders a line chart of AI analysis ratings over time."""
    st.markdown("---")
    st.markdown("<h2>📈 Your Analysis History</h2>", unsafe_allow_html=True)
    
    history = st.session_state.get("analysis_history", [])
    
    ai_analyses = [
        entry for entry in history 
        if entry.get("type") == "deep_ai_concise" and entry.get("rating") is not None
    ]
    
    if len(ai_analyses) < 2:
        st_themed_callout("Run at least two 'PRO AI' analyses to see your progress chart.", level="info")
        return

    try:
        df = pd.DataFrame(ai_analyses)
        df['timestamp'] = pd.to_datetime(df['ts'])
        df = df.sort_values(by='timestamp')
        
        df['Rating (%)'] = df['rating'] * 20
        
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['Rating (%)'],
            mode='lines+markers',
            name='Routine Rating',
            line=dict(color='var(--color-accent-purple)', width=3),
            marker=dict(color='var(--color-accent-purple)', size=8, line=dict(color='var(--color-bg-card)', width=2))
        ))

        fig.update_layout(
            title="PRO AI Routine Rating Over Time",
            xaxis_title="Date of Analysis",
            yaxis_title="Rating (%)",
            yaxis_range=[0, 101],
            font=dict(
                family="var(--font-body)",
                color="var(--color-text-dark)"
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='var(--color-bg-light)',
            xaxis=dict(gridcolor='var(--color-border)'),
            yaxis=dict(gridcolor='var(--color-border)')
        )
        
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st_themed_callout(f"Error generating history graph: {e}", level="error")

# --- Main App Execution ---
def main():
    """Main application flow."""
    initialize_session_state()

    # --- Stylized App Title ---
    st.markdown("""
    <div style="text-align:center; margin-top:0.5rem; margin-bottom:1.25rem;">
        <div style="font-family: 'Lora', serif; color:#957DAD; font-weight:650; letter-spacing:4px; text-transform:uppercase;
                    font-size:clamp(1.0rem, 3.5vw, 2.3rem); text-shadow: 0 6px 20px rgba(149,125,173,0.25);">
            DermacScribe
        </div>
        <div style="font-family: 'Lora', serif; color:#4A3F5E; font-weight:650; letter-spacing:1px;
                    font-size:clamp(2.2rem, 6.1vw, 3.8rem); margin-top:0.3rem; text-shadow: 0 8px 30px rgba(74,63,94,0.08);">
            Combination Analyzer
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Centered Layout ---
    _, col_center, _ = st.columns([1, 4, 1])
    
    with col_center:
        if not db_check():
            st_themed_callout("🚫 **Database Not Found or Invalid!**", level="error")
            st_themed_callout(f"Ensure `{DB_FILE}` exists. Run `python build_database.py` if needed.", level="info")
            st.stop()
        
        render_search_ui()
        st.divider()
        render_current_routine()
        render_analysis_section()
        render_history_graph()

        st.markdown("---")
        st.caption("DermacScribe AI: Smart local search & analysis + optional concise AI insights. Not medical advice.")

if __name__ == "__main__":
    main()