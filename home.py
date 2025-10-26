import streamlit as st
import os
from PIL import Image

# --- Page Configuration ---
st.set_page_config(
    page_title="DermaScribe - Home", 
    layout="wide",
    initial_sidebar_state="auto" # CHANGED: This enables the auto-generated sidebar
)

# --- IMAGE LOADING (LOCAL FILE) ---
# Define the path to your NEW image
# Using os.path.join for better cross-platform compatibility
image_path = os.path.join("C:", os.sep, "Users", "soumy", "OneDrive", "ASUS", "Downloads", "Python-Streamlit", "lavender-themed-skincare-beauty-products-arranged-beautifully-flowers-pastel-packaging-creating-calm-soothing-aesthetic-323793872.webp")

# Function to load the image using Pillow
@st.cache_data # Cache the image loading
def load_local_image(path):
    """Loads an image using Pillow from a local path."""
    if not os.path.exists(path):
        st.error(f"Error: Image file not found at the specified path: {path}")
        print(f"Error: Image file not found at {path}") # Also print to console
        return None
    try:
        # Check if file has read permissions (basic check)
        if not os.access(path, os.R_OK):
            st.error(f"Error: No read permissions for image file at {path}")
            print(f"Error: No read permissions for {path}")
            return None
        return Image.open(path)
    except FileNotFoundError:
        st.error(f"Error: Image file not found at {path}. Please verify the path.")
        print(f"Error: Image file not found at {path}")
        return None
    except Exception as e:
        st.error(f"Error loading image: {e}")
        print(f"Error loading image: {e}")
        return None

hero_image = load_local_image(image_path)


# --- STYLING (CSS updated for logo and nav hover) ---
# --- STYLING (CSS updated for logo and nav hover) ---
def load_css():
    st.markdown("""
    <style>
        /* Import Google Fonts - Lora (Headings) and Montserrat (Body) */
        @import url('https.googleapis.com/css2?family=Lora:wght@500;600;700&family=Montserrat:wght@300;400;500;600&display=swap');

        /* "DermaScribe" Palette (Unchanged) */
        :root {
            --color-bg-light: #FDFBFF;     /* Soft Off-White */
            --color-bg-card: #FFFFFF;       /* White */
            --color-text-dark: #4A3F5E;    /* Dark Purple/Gray */
            --color-text-medium: #6D617A;   /* Medium Purple/Gray */
            --color-accent-purple: #957DAD; /* Elegant Purple */
            --color-gradient-start: #FFD1DC; /* Soft Pink */
            --color-gradient-end: #E0BBE4;   /* Soft Lavender */
            --color-border: #EAE6F0;       /* Light Purple/Gray Border */

            --font-heading: 'Lora', serif;
            --font-body: 'Montserrat', sans-serif;
            --gradient-main: linear-gradient(135deg, var(--color-gradient-start) 0%, var(--color-gradient-end) 100%);
            --gradient-selected-bg: linear-gradient(135deg, #FFC0CB 0%, #DDA0DD 100%); /* Stronger gradient for selected */
        }

        /* --- Global Styles --- */
        html, body, .stApp { font-family: var(--font-body); color: var(--color-text-medium); background-color: var(--color-bg-light); }
        .main .block-container { padding: 3rem 5rem; }
        header, footer { visibility: hidden; height: 0px !important; }
        h1, h2, h3, h4, h5, h6 { font-family: var(--font-heading); color: var(--color-text-dark); font-weight: 600; }
        h1 { font-size: 3.5rem; } h2 { font-size: 2.5rem; margin-bottom: 2rem;} h3 { font-size: 1.8rem; }

        /* --- Header --- */
        .stApp > div:nth-child(1) > div > div > div > div > .st-emotion-cache-13ln4pb {
            border-bottom: 1px solid var(--color-border); padding: 1rem 5rem !important;
            background-color: var(--color-bg-card); position: sticky; top: 0; z-index: 1000; box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        }
        
        /* --- FIX: Header Logo (Added !important to font properties) --- */
        .stApp > div:nth-child(1) .stButton button[key="nav_logo"] {
            font-family: var(--font-heading) !important; 
            font-size: 3.0rem !important; 
            font-weight: 700 !important; 
            color: var(--color-text-dark) !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            line-height: 3.2rem !important; 
            text-transform: none !important; 
            letter-spacing: normal !important; 
            transition: color 0.2s ease; 
        }
        .stApp > div:nth-child(1) .stButton button[key="nav_logo"]:hover {
            color: var(--color-accent-purple) !important;
            transform: none !important;
        }

        /* --- NEW/AGGRESSIVE FIX: Target the text span inside the button --- */
        /* This forces the font styles onto the text element itself */
        .stApp > div:nth-child(1) .stButton button[key="nav_logo"] span {
            font-family: var(--font-heading) !important; 
            font-size: 3.0rem !important; 
            font-weight: 700 !important; 
            line-height: 3.2rem !important;
            color: var(--color-text-dark) !important; /* Ensure span color matches */
            transition: color 0.2s ease; /* Add transition to span too */
        }
        /* --- NEW: Handle hover on the span as well --- */
        .stApp > div:nth-child(1) .stButton button[key="nav_logo"]:hover span {
            color: var(--color-accent-purple) !important;
        }


        /* --- NEW: Header Nav Links (Hover Underline) --- */
        /* These rules are kept for styling other header buttons if you add them,
           but the main nav buttons are removed from render_header() */
        .stApp > div:nth-child(1) .stButton button:not([key="nav_logo"]) { /* Header Nav */
            background: transparent !important; 
            color: var(--color-text-medium) !important; 
            border: none !important; 
            box-shadow: none !important;
            font-family: var(--font-body); 
            font-weight: 600; 
            text-transform: uppercase; 
            font-size: 0.95rem; 
            padding: 0.75rem 0 0.5rem 0 !important; /* Adjusted padding for line */
            border-radius: 0 !important; 
            transition: color 0.2s ease;
            border-bottom: 3px solid transparent !important; /* Holds space for line */
        }
        
        /* Nav Link Hover State */
        .stApp > div:nth-child(1) .stButton button:not([key="nav_logo"]):hover { 
            color: var(--color-accent-purple) !important; 
            transform: none !important; 
            border-bottom: 3px solid var(--color-accent-purple) !important; /* Show line on hover */
        }

        /* Nav Link Active State (Selected) */
        .stApp > div:nth-child(1) .stButton button:not([kind="secondary"]):not([key="nav_logo"]) { 
            color: var(--color-accent-purple) !important; 
            border-bottom: 3px solid var(--color-accent-purple) !important; /* Show line when active */
        }

        /* --- All other CSS rules (Main Buttons, Cards, Quiz, etc.) are kept... --- */
        /* --- ... all your other styles ... --- */
        
        /* --- Main Buttons (Primary Gradient) --- */
        .main .stButton button:not([kind="secondary"]) {
            background: var(--gradient-main); color: var(--color-text-dark); font-family: var(--font-body); font-weight: 600; padding: 0.8rem 2.2rem;
            border-radius: 30px; border: none; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(149, 125, 173, 0.3);
            text-transform: uppercase; letter-spacing: 0.5px;
        }
        .main .stButton button:not([kind="secondary"]):hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(149, 125, 173, 0.4); }
        .main .stButton button:not([kind="secondary"]):disabled { background: var(--color-border) !important; color: var(--color-text-medium) !important; box-shadow: none !important; cursor: not-allowed !important;}


        /* --- Main Buttons (Secondary Outline) --- */
        .main .stButton button[kind="secondary"] {
            background-color: transparent; color: var(--color-accent-purple); font-family: var(--font-body); font-weight: 600; padding: 0.8rem 2.2rem;
            border-radius: 30px; border: 2px solid var(--color-accent-purple); transition: all 0.3s ease; box-shadow: none;
            text-transform: uppercase; letter-spacing: 0.5px;
        }
        .main .stButton button[kind="secondary"]:hover { background-color: var(--color-accent-purple); color: var(--color-bg-card); transform: translateY(-2px); }

        /* --- Base Card --- */
        .card-container { background-color: var(--color-bg-card); border-radius: 20px; padding: 2.5rem; border: 1px solid var(--color-border); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05); }

        /* --- Quiz UI --- */
        .quiz-question-text { font-size: 1.8rem; font-family: var(--font-heading); font-weight: 600; color: var(--color-text-dark); text-align: center; margin-bottom: 2.5rem; }

        /* --- QUIZ BUTTONS --- */
        .quiz-options-grid .stButton button { border-radius: 15px !important; padding: 1.5rem 1rem !important; font-family: var(--font-body) !important; font-weight: 500 !important; text-transform: none !important; letter-spacing: 0 !important; height: 100% !important; line-height: 1.4 !important; font-size: 1rem !important; transition: all 0.2s ease !important; }
        /* Unselected Button */
        .quiz-options-grid .stButton button[kind="secondary"] { background-color: var(--color-bg-light) !important; color: var(--color-text-dark) !important; border: 1px solid var(--color-border) !important; box-shadow: none !important; }
        .quiz-options-grid .stButton button[kind="secondary"]:hover { border-color: var(--color-accent-purple) !important; color: var(--color-accent-purple) !important; transform: none !important; background-color: #FAF7FF !important; }
        /* Selected Button (WHITE background, PURPLE border/text) - OVERRIDING PRIMARY */
        .quiz-options-grid .stButton button[kind="primary"] {
            background: white !important; /* CHANGED */
            color: var(--color-accent-purple) !important; /* CHANGED */
            border: 2px solid var(--color-accent-purple) !important; /* CHANGED */
            font-weight: 600 !important;
            box-shadow: 0 4px 15px rgba(149, 125, 173, 0.2) !important;
            /* Prevent hover effect when selected */
            transform: none !important;
        }
        /* Explicitly style hover for primary to remove gradient hover */
        .quiz-options-grid .stButton button[kind="primary"]:hover {
            background: white !important; /* Keep white */
            color: var(--color-accent-purple) !important; /* Keep purple text */
            transform: none !important; /* No lift */
            box-shadow: 0 4px 15px rgba(149, 125, 173, 0.2) !important; /* Keep shadow */
        }


        /* --- Radio Styling --- */
        .stRadio > label { display: none; }
        .stRadio > div[role="radiogroup"] { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
        .stRadio > div[role="radiogroup"] > label { background-color: var(--color-bg-light); color: var(--color-text-dark); font-family: var(--font-body); font-weight: 500; border: 1px solid var(--color-border); padding: 1.5rem 1rem; border-radius: 15px; text-transform: none; transition: all 0.2s ease; cursor: pointer; text-align: center; line-height: 1.4; font-size: 1rem; }
        /* Selected Radio (WHITE background, PURPLE border/text) */
        .stRadio > div[role="radiogroup"] > label[data-baseweb="radio"]:has(input:checked) {
            background: white !important; /* CHANGED */
            color: var(--color-accent-purple) !important; /* CHANGED */
            border: 2px solid var(--color-accent-purple) !important; /* CHANGED */
            font-weight: 600; box-shadow: 0 4px 15px rgba(149, 125, 173, 0.2);
        }
        .stRadio > div[role="radiogroup"] > label:hover { border-color: var(--color-accent-purple); color: var(--color-accent-purple); background-color: #FAF7FF !important; }

        /* --- Select Slider Styling --- */
        .stSelectSlider > label { display: none; }
        .stSelectSlider [data-basewab="slider"] > div:nth-child(2) { background: var(--gradient-stronger); } /* Track Fill */
        .stSelectSlider [data-basewab="slider"] > div:nth-child(3) { border: 2px solid var(--color-bg-card); background: var(--color-accent-purple); box-shadow: 0 0 10px var(--color-accent-purple); height: 20px; width: 20px; } /* Thumb */
        .stSelectSlider [data-basewab="slider"] > div:nth-child(1) div { font-family: var(--font-body); color: var(--color-text-medium); } /* Labels */

        /* --- Tabs --- */
        .stTabs { border: none; }
        .stTabs [role="tablist"] { border-bottom: 2px solid var(--color-border); gap: 2rem; }
        .stTabs [role="tab"] { font-family: var(--font-heading); font-weight: 600; font-size: 1.2rem; color: var(--color-text-medium); border: none; background: none; padding-bottom: 1rem; }
        .stTabs [aria-selected="true"] { color: var(--color-accent-purple); border-bottom: 2px solid var(--color-accent-purple); }
        .stTabs [role="tab"]:hover { color: var(--color-accent-purple); }
        .stTabs [role="tabpanel"] { padding: 2rem 0; }

        /* --- Results Page --- */
        .score-display { font-family: var(--font-heading); font-size: 6rem; font-weight: 700; color: var(--color-accent-purple); line-height: 1; }
        .result-container h3 { margin-top: 1.5rem; }
        .result-container p { font-size: 1rem; color: var(--color-text-medium); }
        .result-container strong span { background: var(--gradient-main); -webkit-background-clip: text; color: transparent; font-weight: 700; }

        /* --- Home Page --- */
        .home-section-card { background-color: var(--color-bg-card); border-radius: 20px; padding: 2.5rem; border: 1px solid var(--color-border); margin-top: 3rem; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05); }
        .feature-box { background-color: var(--color-bg-light); border-radius: 15px; padding: 2rem; height: 100%; border: 1px solid var(--color-border); text-align: left; }
        .feature-box h3 { font-size: 1.3rem; color: var(--color-text-dark); margin-bottom: 1rem; text-align: center; }
        .feature-box p { color: var(--color-text-medium); font-size: 1rem; text-align: center; }

        /* --- History Page --- */
        .history-card { background-color: var(--color-bg-card); border-radius: 15px; padding: 1.5rem 2rem; border: 1px solid var(--color-border); margin-bottom: 1rem; box-shadow: 0 5px 15px rgba(0,0,0,0.03); }
        .history-card .history-score { font-family: var(--font-heading); font-size: 3rem; color: var(--color-accent-purple); line-height: 1; font-weight: 700; }
        .history-card .history-date { font-size: 0.9rem; color: var(--color-text-medium); }
        .history-card .stExpander { border: none; background-color: transparent; margin-top: 1rem; box-shadow: none;}
        .history-card .stExpander summary { font-family: var(--font-body); font-weight: 600; color: var(--color-accent-purple); font-size: 1rem; text-transform: uppercase; letter-spacing: 0.5px; }
        .history-card .stExpander summary:hover { color: var(--color-text-dark); }

        /* --- Icons --- */
        .stIcon { vertical-align: middle; }

    </style>
    """, unsafe_allow_html=True)

def init_session_state():
    # 'page' session state is no longer needed for navigation
    if 'is_on_tour' not in st.session_state:
        st.session_state.is_on_tour = False

# NEW: Function to start the tour
def start_tour():
    st.session_state.is_on_tour = True
    # This can be expanded later to show popups or guides.
    st.toast("Let's start the tour! (Feature coming soon)")

# --- HEADER (Simplified) ---
def render_header():
    with st.container():
        # We keep the column layout to ensure the CSS for the logo still works
        cols = st.columns([1, 2])
        with cols[0]:
            # The logo button doesn't need an on_click, as it's on the home page
            st.button("DermaScribe", on_click=None, key="nav_logo")
        with cols[1]:
            # All navigation buttons have been REMOVED.
            # The sidebar (auto-generated from the 'pages/' folder)
            # now handles all app navigation.
            pass

# --- PAGE RENDERING FUNCTION (Only Welcome Page) ---
def show_welcome_page():
    # --- Hero Section (Text + Image) ---
    hero_cols = st.columns([1, 1])
    with hero_cols[0]:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style="padding-top: 1rem; text-align: left;">
                <h1 style="text-align: left; font-size: 3rem;">DISCOVER YOUR RADIANCE!</h1>
                <p style="font-size: 1.2rem; color: var(--color-text-medium); margin: 1rem 0 2rem 0; max-width: 600px;">
                    Welcome to DermaScribe. Understand your skin's needs in minutes and unlock personalized insights for a healthier, more radiant complexion.
                </p>
            </div>
            """, unsafe_allow_html=True)
    with hero_cols[1]:
        if hero_image:
            st.image(hero_image, use_container_width=True, caption="Achieve your best skin")
        else:
            st.markdown('<div style="height: 400px; display: flex; align-items: center; justify-content: center; background: var(--color-border); border-radius: 15px;"><p style="color: var(--color-text-medium);">Hero image could not be loaded. Please check file path in code.</p></div>', unsafe_allow_html=True)

    st.markdown("<br><br><hr style='border-color: var(--color-border);'><br>", unsafe_allow_html=True)

    # --- NEW: Feature 2: Product Analyzer (Image + Text) ---
    analyzer_cols = st.columns([1, 1])
    with analyzer_cols[0]:
        if hero_image:
            st.image(hero_image, use_container_width=True, caption="Analyze Your Skincare Routine")
        else:
            st.markdown('<div style="height: 400px; display: flex; align-items: center; justify-content: center; background: var(--color-border); border-radius: 15px;"><p style="color: var(--color-text-medium);">Image placeholder</p></div>', unsafe_allow_html=True)

    with analyzer_cols[1]:
        # --- FIX: Separated Markdown from Button ---
        st.markdown(f"""
        <div style="padding: 2rem; text-align: left; height: 100%; display: flex; flex-direction: column; justify-content: center;">
            <h2 style="text-align: left;">Check Your Products Routine for Conflicts</h2>
            <p style="font-size: 1.1rem; color: var(--color-text-medium); margin: 1rem 0 2rem 0;">
                Eliminate the guesswork. Our <strong>Product Analyzer</strong> instantly cross-references every item in your routine to flag potential conflicts or harmful combinations. Ensure your regimen is perfectly safe and effective.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # The button is now called after the markdown, and wrapped in a div for styling
        st.markdown('<div style="padding: 0 2rem; max-width: 320px;">', unsafe_allow_html=True)
        # This button should ideally navigate to the 'Product Analyzer' page.
        # Since this is a bit more complex, for now it just sits here.
        # A better approach would be: st.page_link("pages/1_Product_Analyzer.py", label="🧪 ANALYZE YOUR PRODUCTS")
        # But we'll keep your button style for now.
        st.button("🧪 ANALYZE YOUR PRODUCTS", on_click=None, type="primary", use_container_width=True, key="btn_analyzer")
        st.markdown('</div>', unsafe_allow_html=True)
        # --- END FIX ---

    st.markdown("<br><br><hr style='border-color: var(--color-border);'><br>", unsafe_allow_html=True)
    
    # --- NEW: Feature 3: AI Face Scan (Text + Image) ---
    facescan_cols = st.columns([1, 1])
    with facescan_cols[0]:
        # --- FIX: Separated Markdown from Button ---
        st.markdown(f"""
        <div style="padding: 2rem; text-align: left; height: 100%; display: flex; flex-direction: column; justify-content: center;">
            <h2 style="text-align: left;">Get Hyper-Personalized Advice</h2>
            <p style="font-size: 1.1rem; color: var(--color-text-medium); margin: 1rem 0 2rem 0;">
                Go beyond generic advice. Our <strong>FaceScan AI</strong> provides hyper-personalized recommendations. Using advanced computer vision, it analyzes your skin's unique needs to guide you to the perfect products. It's your personal skin expert, on demand.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # The button is now called after the markdown
        st.markdown('<div style="padding: 0 2rem; max-width: 320px;">', unsafe_allow_html=True)
        st.button("📸 SCAN YOUR SKIN", on_click=None, type="primary", use_container_width=True, key="btn_facescan")
        st.markdown('</div>', unsafe_allow_html=True)
        # --- END FIX ---
    
    with facescan_cols[1]:
        if hero_image:
            st.image(hero_image, use_container_width=True, caption="Discover Personalized Recommendations")
        else:
            st.markdown('<div style="height: 400px; display: flex; align-items: center; justify-content: center; background: var(--color-border); border-radius: 15px;"><p style="color: var(--color-text-medium);">Image placeholder</p></div>', unsafe_allow_html=True)

    st.markdown("<br><br><hr style='border-color: var(--color-border);'><br>", unsafe_allow_html=True)

    # --- NEW: CTA: Take a Tour ---
    # --- FIX: Separated Markdown from Button ---
    st.markdown(f"""
    <div style="padding: 4rem 2rem 0 2rem; text-align: center; background: var(--color-bg-light);">
        <h2 style="text-align: center;">New to DermaScribe?</h2>
        <p style="font-size: 1.2rem; color: var(--color-text-medium); margin: 1rem auto 2rem auto; max-width: 600px;">
            Not sure where to begin? Take a guided tour to discover all the features and start your journey to healthier skin.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # The button is now called after the markdown
    st.markdown('<div style="max-width: 300px; margin: 0 auto; padding-bottom: 4rem; text-align: center; background: var(--color-bg-light);">', unsafe_allow_html=True)
    st.button("✨ Take a Test!", on_click=start_tour, type="primary", use_container_width=True, key="btn_tour")
    st.markdown('</div>', unsafe_allow_html=True)
    # --- END FIX ---


# --- MAIN APP LOGIC ---
load_css()
init_session_state()
render_header()

# This file now only shows the welcome page.
# Streamlit handles navigation to the other pages in the 'pages/' folder.
show_welcome_page()