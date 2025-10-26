import streamlit as st
import json
import os  # <-- Import OS for image path
from PIL import Image  # <-- Import Pillow for image loading

# ------------------Highlight new there so like to stream plate. Au. Living in your main content heading you know, AI, machine learning, front end reuse. But. I. I. ---------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Ingredient Glossary",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------
# 2. AURORA GLOW THEME CSS (BOX COLORS UPDATED TO PURPLE)
# ---------------------------------------------------------------------

def load_css():
    """Loads the complete Aurora Glow CSS theme with robust selectors."""
    st.markdown("""
    <style>
        /* Import Google Fonts - Lora (Headings) and Montserrat (Body) */
        @import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;600;700&family=Montserrat:wght@300;400;500;600&family=Source+Sans+Pro:wght@400;600;700&display=swap');

        /* "Aurora Glow" Palette */
        :root {
            --color-bg-light: #FDFBFF;     /* Soft Off-White */
            --color-bg-card: #FFFFFF;       /* White */
            --color-text-dark: #4A3F5E;    /* Dark Purple/Gray */
            --color-text-medium: #6D617A;   /* Medium Purple/Gray */
            --color-accent-purple: #957DAD; /* Elegant Purple */
            --color-gradient-start: #FFD1DC; /* Soft Pink */
            --color-gradient-end: #E0BBE4;   /* Soft Lavender */
            --color-border: #EAE6F0;       /* Light Purple/Gray Border */

            /* --- FONT UPDATED: Lora for main titles, Source Sans Pro for content headings --- */
            --font-heading-main: 'Lora', serif; /* For main page title */
            --font-heading-content: 'Source Sans Pro', sans-serif; /* For ingredient names */
            --font-body: 'Montserrat', sans-serif;
            --gradient-main: linear-gradient(135deg, var(--color-gradient-start) 0%, var(--color-gradient-end) 100%);
        }

        /* --- Global Styles --- */
        html, body, .stApp { 
            font-family: var(--font-body); 
            color: var(--color-text-medium); 
            background-color: var(--color-bg-light); 
        }
        .main .block-container { 
            padding: 2rem 5rem 5rem 5rem;
        }
        header, footer { 
            visibility: hidden; 
            height: 0px !important; 
        }
        h1, h2, h3, h4, h5, h6 { 
            font-family: var(--font-heading-main); /* Use Lora for general headings */
            color: var(--color-text-dark); 
            font-weight: 600; 
        }
        /* Decreased heading font sizes slightly */
        h1 { font-size: 3.2rem; } 
        h2 { font-size: 2.3rem; margin-bottom: 2rem;} 
        h3 { font-size: 1.7rem; }
        
        /* --- Base Card (Used for search box) --- */
        .card-container { 
            background-color: var(--color-bg-card); 
            border-radius: 20px; 
            padding: 2.5rem; 
            border: 1px solid var(--color-border); 
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05); 
            margin-bottom: 2rem;
        }
        
        /* --- Divider --- */
        hr {
            border-top: 1px solid var(--color-border);
            margin: 1.5rem 0;
        }
        
        /* --- Form Element Styling --- */
        .stTextInput label, .stMultiSelect label {
            font-family: var(--font-heading-content); /* Use Source Sans Pro */
            color: var(--color-text-dark);
            font-weight: 600;
            font-size: 1.0rem; /* DECREASED */
            margin-bottom: 0.5rem;
        }
        
        /* Text Input */
        .stTextInput div[data-baseweb="input"] > div {
            background-color: var(--color-bg-light);
            border: 1px solid var(--color-border);
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.03);
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }
        .stTextInput input {
            font-family: var(--font-body);
            color: var(--color-text-dark);
        }
        .stTextInput div[data-baseweb="input"] > div:focus-within {
            border-color: var(--color-accent-purple) !important;
            box-shadow: 0 0 0 3px rgba(149, 125, 173, 0.15) !important;
        }
        
        /* Multiselect */
        .stMultiSelect div[data-baseweb="select"] > div {
            background-color: var(--color-bg-light);
            border: 1px solid var(--color-border);
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.03);
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }
        .stMultiSelect div[data-baseweb="select"] > div:focus-within {
             border-color: var(--color-accent-purple) !important;
             box-shadow: 0 0 0 3px rgba(149, 125, 173, 0.15) !important;
        }
        .stMultiSelect span[data-baseweb="tag"] {
            background: var(--gradient-main);
            color: var(--color-text-dark);
            font-weight: 500;
            border-radius: 5px;
            padding: 0.25rem 0.6rem;
        }
        .stMultiSelect span[data-baseweb="tag"] > span {
             color: var(--color-text-dark);
        }
        
        /* --- ROBUST Expander Styling (FONT WEIGHT DECREASED) --- */
        div[data-testid="stExpander"] {
            background-color: var(--color-bg-card) !important;
            border: 1px solid var(--color-border) !important;
            border-radius: 15px !important; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.03) !important;
            margin-bottom: 1rem !important; 
            transition: box-shadow 0.2s ease;
        }
        div[data-testid="stExpander"]:hover {
             box-shadow: 0 8px 25px rgba(149, 125, 173, 0.1) !important;
        }
        div[data-testid="stExpander"] summary {
             transition: color 0.2s ease;
             padding: 0.5rem 0; 
        }
        /* This targets the text <p> tag inside the summary */
        div[data-testid="stExpander"] summary p {
             font-family: var(--font-heading-content) !important; /* CHANGED to Source Sans Pro */
             font-weight: 600 !important; /* DECREASED from 700 */
             font-size: 1.15rem !important; 
             letter-spacing: 0.2px !important;
             color: var(--color-text-dark) !important;
             transition: color 0.2s ease !important;
        }
        div[data-testid="stExpander"] summary:hover p {
             color: var(--color-accent-purple) !important;
        }
        div[data-testid="stExpander"] [data-baseweb="block"] {
             padding-top: 1.5rem !important; 
        }
        
        /* --- ROBUST Style for st.info and st.warning (CHANGED TO PURPLE) --- */
        
        /* Target st.info (Pro Tip) */
        div[data-testid="stInfo"] {
            background-color: #F6F4FF !important; /* Light Purple */
            border-radius: 12px !important;
            border: 1px solid var(--color-border) !important; /* Light border */
            box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
            font-family: var(--font-body) !important; 
        }
        div[data-testid="stInfo"] div {
            color: #4B3F6B !important; /* Darker Purple */
            font-size: 0.95rem !important;
        }

        /* Target st.warning (Good to Know) */
        div[data-testid="stWarning"] {
            background-color: #F6F4FF !important; /* Light Purple */
            border-radius: 12px !important;
            border: 1px solid var(--color-border) !important; /* Light border */
            box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
            font-family: var(--font-body) !important; 
        }
        div[data-testid="stWarning"] div {
            color: #4B3F6B !important; /* Darker Purple */
            font-size: 0.95rem !important; 
        }
        
        /* --- Custom Box for "What it is" (CHANGED TO PURPLE) --- */
        .info-box-custom {
            background-color: #F6F4FF !important; /* Light Purple */
            border-radius: 12px !important;
            border: 1px solid var(--color-border) !important; /* Light border */
            box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
            padding: 1rem 1.25rem !important;
            margin-bottom: 1rem;
            font-family: var(--font-body) !important;
            color: #4B3F6B !important; /* Darker Purple */
            font-size: 0.95rem !important;
            line-height: 1.6;
        }
        .info-box-custom strong {
            color: #4B3F6B !important;
            font-weight: 600;
        }

        /* --- Title for tag lists (Pairs, Clashes) (FONT CHANGED) --- */
        .tag-title {
            font-family: var(--font-heading-content); /* CHANGED to Source Sans Pro */
            font-weight: 600;
            font-size: 1.0rem; /* DECREASED from 1.1rem */
            color: var(--color-text-dark);
            margin-bottom: 0.5rem;
        }

        /* --- Styling for "Best Time to Use" text (FONT SIZE DECREASED) --- */
        .detail-text {
            font-family: var(--font-body);
            font-size: 0.95rem; /* DECREASED from 1.0rem */
            color: var(--color-text-medium);
            margin-bottom: 1rem;
        }
        .detail-text strong {
            font-weight: 600;
            color: var(--color-text-dark);
        }
        
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------
# 3. IMAGE LOADING
# ---------------------------------------------------------------------

# !! IMPORTANT: This is the exact hardcoded path from your quiz file.
# !! This will ONLY work on your computer.
image_path = os.path.join("C:", os.sep, "Users", "soumy", "OneDrive", "ASUS", "Downloads", "Python-Streamlit", "lavender-themed-skincare-beauty-products-arranged-beautifully-flowers-pastel-packaging-creating-calm-soothing-aesthetic-323793872.webp")

@st.cache_data
def load_local_image(path):
    """Loads an image using Pillow from a local path."""
    if not os.path.exists(path):
        st.error(f"Error: Image file not found at the specified path: {path}")
        print(f"Error: Image file not found at {path}")
        return None
    try:
        return Image.open(path)
    except Exception as e:
        st.error(f"Error loading image: {e}")
        print(f"Error loading image: {e}")
        return None

# Load the hero image
hero_image = load_local_image(image_path)


# ---------------------------------------------------------------------
# 4. LOAD DATABASE FROM JSON FILE (*** UPDATED ***)
# ---------------------------------------------------------------------

@st.cache_data
def load_database():
    """Loads the ingredient database from the JSON file."""
    
    # --- THIS IS THE UPDATED FILE NAME ---
    # Use absolute path to ensure file is found regardless of working directory
    JSON_FILE_NAME = os.path.join(os.path.dirname(__file__), "ingredient_db.json")
    # -------------------------------------

    try:
        # 'utf-8' encoding is good for special characters
        with open(JSON_FILE_NAME, 'r', encoding='utf-8') as f:
            rules_data = json.load(f)
        
        # We only need the "ingredient_profiles" part for this page
        ingredient_db = rules_data.get("ingredient_profiles", {})
        
        if not ingredient_db:
            st.error(f"Error: 'ingredient_profiles' not found or is empty in {JSON_FILE_NAME}.")
            return {}
        return ingredient_db
        
    except FileNotFoundError:
        st.error(f"Fatal Error: `{JSON_FILE_NAME}` file not found. Make sure it's in the same directory.")
        return {} # Return empty dict to prevent app crash
    except json.JSONDecodeError:
        st.error(f"Fatal Error: Could not read `{JSON_FILE_NAME}`. Check for syntax errors (e.g., missing comma).")
        return {}
    except Exception as e:
        st.error(f"An unexpected error occurred loading the database: {e}")
        return {}

# Load the database once
INGREDIENT_DB = load_database()

# ---------------------------------------------------------------------
# 5. HELPER FUNCTIONS (Tag Palette Updated, FONT SIZE DECREASED)
# ---------------------------------------------------------------------

@st.cache_data
def get_all_concerns(db):
    """Gets a unique, sorted list of all concerns from the DB."""
    all_concerns = set()
    for details in db.values():
        for concern in details.get("concerns_targeted", []):
            all_concerns.add(concern.replace("_", " ").title()) 
    return sorted(list(all_concerns))

def display_list_as_tags(title, items_list, item_type='neutral'):
    """Helper function to display a list of items with themed tags."""
    if items_list:
        st.markdown(f"<div class='tag-title'>{title}</div>", unsafe_allow_html=True)
        
        # --- UPDATED COLOR PALETTE ---
        if item_type == 'error':
            # Red -> Dull White
            bg = "#FDFBFF"; border = "#EAE6F0"; text = "#6D617A" 
        elif item_type == 'success':
            # Green -> Lavender (This is the light purple)
            bg = "#F6F4FF"; border = "#EAE6F0"; text = "#4B3F6B"
        else: 
            # Neutral -> Light Pink
            bg = "#FFF0F5"; border = "#FFDDE9"; text = "#AD597B"
        
        tags_html = "".join([
            f"""<span style='
                background-color: {bg}; 
                border: 1px solid {border}; 
                color: {text};
                font-family: var(--font-body);
                font-weight: 500;
                font-size: 0.85rem; /* DECREASED from 0.9rem */
                border-radius: 5px; 
                padding: 4px 10px; 
                margin: 3px; 
                display: inline-block;'>
                {item.replace('_', ' ').title()}
            </span>""" 
            for item in items_list
        ])
        
        st.markdown(f"<div style='line-height: 1.8;'>{tags_html}</div>", unsafe_allow_html=True)
    else:
        placeholder_text = ""
        if item_type == 'error':
            placeholder_text = "None listed"
        elif item_type == 'success':
            placeholder_text = "Works with most ingredients!"
        
        if placeholder_text:
            st.markdown(f"<div class='tag-title'>{title}</div>", unsafe_allow_html=True)
            st.markdown(f"<span style='color: #888; font-style: italic;'>{placeholder_text}</span>", unsafe_allow_html=True)


# ---------------------------------------------------------------------
# 6. MAIN PAGE FUNCTION (HEADER UPDATED, NEW FEATURE ADDED)
# ---------------------------------------------------------------------

def run_glossary_app():
    """The main function to run the Streamlit page."""
    
    # --- HEADER (STYLED LIKE TESTUI.PY) ---
    st.markdown("""
    <div style="text-align:center; margin-top:0.5rem; margin-bottom:1.25rem;">
        <div style="font-family: var(--font-heading-main); color:#957DAD; font-weight:650; letter-spacing:4px; text-transform:uppercase;
                    font-size:clamp(1.0rem, 3.5vw, 2.0rem); text-shadow: 0 6px 20px rgba(149,125,173,0.25);">
            DermacScribe
        </div>
        <div style="font-family: var(--font-heading-main); color:#4A3F5E; font-weight:650; letter-spacing:1px;
                    font-size:clamp(2.0rem, 6.1vw, 3.2rem); margin-top:0.3rem; text-shadow: 0 8px 30px rgba(74,63,94,0.08);">
            The Ingredient Glossary
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<p style='text-align: center; font-size: 1.1rem; color: var(--color-text-medium); max-width: 700px; margin: -1rem auto 2rem auto;'>Search our database to understand what's in your products, what it does, and how to use it safely.</p>", unsafe_allow_html=True)

    # --- Hero Image ---
    if hero_image:
        _ , img_col, _ = st.columns([1, 4, 1])
        with img_col:
            st.image(hero_image, use_container_width=True, caption="Skincare essentials")
    st.markdown("<br>", unsafe_allow_html=True)

    # Check if DB loaded properly
    if not INGREDIENT_DB:
        # The error message is already shown in load_database(),
        # so we just stop the app here.
        return

    # --- Center the main content ---
    _ , main_col, _ = st.columns([1, 4, 1])
    with main_col:
    
        # --- Search and Filter Bar (in a card) ---
        with st.container():
            # st.markdown('<div class="card-container">', unsafe_allow_html=True)
            st.markdown("<h3 style='margin-top: 0; text-align: center; font-size: 1.5rem; font-family: var(--font-heading-main);'>Find Your Ingredient</h3>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            with col1:
                search_query = st.text_input(
                    "Search by ingredient name", 
                    placeholder="e.g., Retinol, Salicylic Acid, Niacinamide...",
                    label_visibility="collapsed",
                ).lower()

            with col2:
                all_concerns_list = get_all_concerns(INGREDIENT_DB)
                selected_concerns = st.multiselect(
                    "Filter by skin concern",
                    options=all_concerns_list,
                    placeholder="Select concerns...",
                    label_visibility="collapsed",
                )
            st.markdown('</div>', unsafe_allow_html=True)

        # --- NEW FEATURE: PRO TIP (uses st.info, now styled as purple) ---
        st.info("**Pro Tip:** Always patch-test a new ingredient on a small area (like behind your ear or on your inner arm) for 24-48 hours before applying it to your entire face.")


        # --- Filtering Logic (Unchanged) ---
        filtered_db = INGREDIENT_DB.copy()
        if search_query:
            filtered_db = {
                name: details for name, details in filtered_db.items()
                if search_query in name.lower() or search_query in details.get("display_name", "").lower()
            }
        if selected_concerns:
            selected_concerns_lower = [concern.lower().replace(" ", "_") for concern in selected_concerns]
            filtered_db = {
                name: details for name, details in filtered_db.items()
                if any(concern in details.get("concerns_targeted", []) for concern in selected_concerns_lower)
            }

        # --- Display Results ---
        st.markdown("---") # Themed <hr>

        if not filtered_db:
            # Use st.info for a softer, on-theme "no results" message
            st.info("No ingredients match your criteria. Try adjusting your search or filters.")
        else:
            count_text = "1 matching ingredient" if len(filtered_db) == 1 else f"{len(filtered_db)} matching ingredients"
            st.markdown(f"#### Displaying {count_text}...")
            
            sorted_ingredients = sorted(filtered_db.items())
            
            for ingredient_key, details in sorted_ingredients:
                
                display_name = details.get("display_name", ingredient_key.title())
                ingredient_type = details.get("type", "Ingredient").replace("_", " ").title()

                # Python f-string is used for the label, CSS handles the styling
                expander_label = f"{display_name} ({ingredient_type})"
                
                with st.expander(expander_label):
                    col_info, col_pair_clash = st.columns([2, 1])
                    
                    with col_info:
                        # --- UPDATED: Use custom HTML box (now styled as purple) ---
                        description = details.get('description', 'No description available for this ingredient yet.')
                        st.markdown(f"<div class='info-box-custom'><strong>What it is:</strong> {description}</div>", unsafe_allow_html=True)
                        
                        if details.get('warning'):
                            # This will ALSO now be a purple box (styled via st.warning CSS)
                            st.warning(f"**Good to Know:** {details.get('warning')}")
                        
                        best_time = details.get('best_time', 'AM / PM')
                        st.markdown(f"<div class='detail-text'><strong>Best Time to Use:</strong> {best_time}</div>", unsafe_allow_html=True)
                        
                        # This will now be pink tags
                        display_list_as_tags("Targets Concerns:", details.get('concerns_targeted', []), 'neutral')

                    with col_pair_clash:
                        # This will be lavender (light purple) tags
                        display_list_as_tags("Pairs Well With", details.get('pairs_well_with', []), 'success')
                        st.markdown("<br>", unsafe_allow_html=True) 
                        # This will be dull white tags
                        display_list_as_tags("Clashes With", details.get('conflicts_with', []), 'error')


# ---------------------------------------------------------------------
# 7. APP EXECUTION
# ---------------------------------------------------------------------

# Load the CSS first
load_css()

if __name__ == "__main__":
    run_glossary_app()