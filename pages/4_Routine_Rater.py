import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import altair as alt

# --- STYLING (CSS with "Soft Pink" Taskbar) ---
def load_css():
    st.markdown("""
    <style>
        /* Import Google Fonts - Lora (Headings) and Montserrat (Body) */
        @import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;600;700&family=Montserrat:wght@300;400;500;600&display=swap');

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

            --font-heading: 'Lora', serif;
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
        h3 { font-size: 1.8rem; }
        
        p, li {
            font-size: 1.1rem;
            color: var(--color-text-medium);
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
        
        /* --- Primary Buttons (Gradients) --- */
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

        /* --- Secondary Buttons (Outlines) --- */
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
        
        /* --- TASKBAR OVERRIDE: "SOFT PINK" --- 
        This is the change you requested.
        It targets the selected (primary) button ONLY inside the taskbar.
        */
        div[data-testid="stHorizontalBlock"] .stButton > button:not([kind="secondary"]) {
            background: #FFD1DC !important; /* Soft Pink */
            color: #4A3F5E !important; /* Dark Purple Text */
            border: 2px solid #FFD1DC !important;
            box-shadow: 0 4px 15px rgba(255, 209, 220, 0.5) !important;
        }
        
        /* --- Quiz UI --- */
        .quiz-question-text { 
            font-size: 1.8rem; 
            font-family: var(--font-heading); 
            font-weight: 600; 
            color: var(--color-text-dark); 
            text-align: center; 
            margin-bottom: 2.5rem; 
        }
        
        /* --- Radio Styling (for selectbox replacement) --- */
        .stRadio > label { /* This is the Question Text */
            font-size: 1.8rem; 
            font-family: var(--font-heading); 
            font-weight: 600; 
            color: var(--color-text-dark); 
            text-align: center; 
            margin-bottom: 2.5rem; 
        }
        .stRadio > div[role="radiogroup"] { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 1rem; 
        }
        .stRadio > div[role="radiogroup"] > label { 
            background-color: var(--color-bg-light); 
            color: var(--color-text-dark); 
            font-family: var(--font-body); 
            font-weight: 500; 
            border: 1px solid var(--color-border); 
            padding: 1.5rem 1rem; 
            border-radius: 15px; 
            text-transform: none; 
            transition: all 0.2s ease; 
            cursor: pointer; 
            text-align: center; 
            line-height: 1.4; 
            font-size: 1rem; 
        }
        /* Selected Radio */
        .stRadio > div[role="radiogroup"] > label[data-baseweb="radio"]:has(input:checked) {
            background: white !important;
            color: var(--color-accent-purple) !important;
            border: 2px solid var(--color-accent-purple) !important;
            font-weight: 600; 
            box-shadow: 0 4px 15px rgba(149, 125, 173, 0.2);
        }
        .stRadio > div[role="radiogroup"] > label:hover { 
            border-color: var(--color-accent-purple); 
            color: var(--color-accent-purple); 
            background-color: #FAF7FF !important; 
        }

        /* --- Select Slider Styling (for slider replacement) --- */
        .stSelectSlider > label { /* This is the Question Text */
            font-size: 1.8rem; 
            font-family: var(--font-heading); 
            font-weight: 600; 
            color: var(--color-text-dark); 
            text-align: center; 
            margin-bottom: 2.5rem; 
        }
        .stSelectSlider [data-baseweb="slider"] > div:nth-child(2) { 
            background: var(--gradient-main); 
        } /* Track Fill */
        .stSelectSlider [data-baseweb="slider"] > div:nth-child(3) { 
            border: 2px solid var(--color-bg-card); 
            background: var(--color-accent-purple); 
            box-shadow: 0 0 10px var(--color-accent-purple); 
            height: 20px; 
            width: 20px; 
        } /* Thumb */
        .stSelectSlider [data-baseweb="slider"] > div:nth-child(1) div { 
            font-family: var(--font-body); 
            color: var(--color-text-medium); 
        } /* Labels */
        
        /* --- Multiselect Question Text --- */
        .multiselect-label {
            font-size: 1.8rem; 
            font-family: var(--font-heading); 
            font-weight: 600; 
            color: var(--color-text-dark); 
            text-align: center; 
            margin-bottom: 1.5rem; 
        }
        
        /* --- Results Page --- */
        .score-display { 
            font-family: var(--font-heading); 
            font-size: 6rem; 
            font-weight: 700; 
            color: var(--color-accent-purple); 
            line-height: 1;
            text-align: center;
        }
        .result-container h3 { 
            margin-top: 1.5rem; 
            font-family: var(--font-heading); 
            font-weight: 600; 
            color: var(--color-text-dark);
            text-align: center;
        }

        /* --- Style info/warning/error boxes --- */
        .stAlert {
            border-radius: 12px;
            border: none;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        .stAlert[data-baseweb="alert"] {
            background-color: #F6F4FF;
        }
        .stAlert[data-baseweb="alert"] > div {
            color: #4B3F6B;
        }
        .stAlert[data-baseweb="alert"].st-error {
            background-color: #FFF0F0;
        }
        .stAlert[data-baseweb="alert"].st-warning {
            background-color: #FFF9E6;
        }
        .stAlert[data-baseweb="alert"].st-success {
            background-color: #F0FFF4;
        }
        
        /* --- Style Charts --- */
        .stPlotlyChart {
            border: 1px solid var(--color-border);
            border-radius: 16px;
            padding: 1rem;
            background-color: #FFFFFF;
        }
        .stAltairChart {
            border: 1px solid var(--color-border);
            border-radius: 16px;
            padding: 1rem;
            background-color: #FFFFFF;
        }

    </style>
    """, unsafe_allow_html=True)

# --- Algorithm Functions ---

def analyze_profile(inputs):
    """
    Analyzes the new profile questions to infer skin type, sensitivity,
    and primary concerns.
    """
    profile = {}
    
    # Infer Type
    if "Tight and dry" in inputs['feeling']:
        profile['Inferred Type'] = "Dry"
    elif "Shiny all over" in inputs['feeling']:
        profile['Inferred Type'] = "Oily"
    elif "Shiny in the T-zone" in inputs['feeling']:
        profile['Inferred Type'] = "Combination"
    else:
        profile['Inferred Type'] = "Normal"
        
    # Infer Sensitivity
    if "Sometimes stings" in inputs['sensitivity']:
        profile['Inferred Sensitivity'] = "High"
    else:
        profile['Inferred Sensitivity'] = "Normal"

    # Infer Concerns
    concerns = []
    if "Frequently" in inputs['breakouts']:
        concerns.append("Acne-Prone")
    if "Often red" in inputs['reactivity']:
        concerns.append("Redness-Prone")
    if "Dull or uneven" in inputs['reactivity']:
        concerns.append("Dullness")
        
    if not concerns:
        concerns.append("General Maintenance")
        
    profile['Inferred Concerns'] = ", ".join(concerns)
    return profile

def calculate_score_and_profile(inputs, profile):
    """
    Calculates the score and generates warnings.
    Returns: total_score (int), category_scores (dict), max_scores (dict), warnings (list), opportunities (list)
    """
    warnings = []
    opportunities = []
    
    # Define score categories
    category_scores = {
        'Sun Protection': 0,
        'Routine & Habits': 0,
        'Internal Health': 0,
        'External Factors': 0
    }
    max_scores = {
        'Sun Protection': 25,
        'Routine & Habits': 30, # Cleansing (10), Actives (10), Exfoliation (10)
        'Internal Health': 30, # Sleep (15), Diet/Water (15)
        'External Factors': 15  # Stress (10), Environment (5)
    }
    
    # 1. Sun Protection (Max 25)
    if inputs['sunscreen'] == 'Every day, rain or shine, and reapply':
        category_scores['Sun Protection'] = 25
    elif inputs['sunscreen'] == 'Most days, when I remember':
        category_scores['Sun Protection'] = 15
        opportunities.append("Make sunscreen a non-negotiable daily habit.")
    elif inputs['sunscreen'] == 'Only on very sunny days':
        category_scores['Sun Protection'] = 5
        warnings.append(("SUNSCREEN_LOW", "UV damage occurs even on cloudy days. Daily use is critical."))
    else: # 'Rarely or never'
        warnings.append(("SUNSCREEN_NONE", "CRITICAL: Skipping sunscreen is the #1 cause of premature aging and skin cancer risk."))

    # 2. Routine & Habits (Max 30)
    # Cleansing (10 pts)
    if inputs['makeup_removal'] == 'I often forget or sleep in it':
        warnings.append(("SLEEP_IN_MAKEUP", "CRITICAL: Sleeping in makeup clogs pores, causes breakouts, and accelerates aging."))
    elif inputs['makeup_removal'] == 'I primarily use makeup wipes':
        category_scores['Routine & Habits'] += 2
        warnings.append(("MAKEUP_WIPES", "Makeup wipes don't properly cleanse and can leave irritating residue."))
    elif inputs['makeup_removal'] == 'I use a single, thorough cleanser':
        category_scores['Routine & Habits'] += 7
        opportunities.append("A single cleanse is good, but a double cleanse (oil/balm first) is more effective for SPF/makeup.")
    else: # Double cleanse
        category_scores['Routine & Habits'] += 10
        
    # Actives (10 pts)
    num_actives = len(inputs.get('actives', []))
    if "I use too many things!" in inputs.get('actives', []):
        warnings.append(("BARRIER_DAMAGE", "CRITICAL: Trying too many new things is a fast track to a damaged skin barrier. STOP all actives."))
    elif num_actives > 3:
        category_scores['Routine & Habits'] += 2
        warnings.append(("TOO_MANY_ACTIVES", "You are using 4+ active ingredients. This is a high risk for irritation."))
    elif 1 <= num_actives <= 3:
        category_scores['Routine & Habits'] += 10 # Ideal
    elif num_actives == 0:
        category_scores['Routine & Habits'] += 5 # Safe
        opportunities.append("Your routine is a great 'basic' canvas. You can now safely introduce *one* active.")

    # Exfoliation (10 pts)
    if "Over-exfoliate (Physical scrubs or acids daily)" in inputs['exfoliation']:
        warnings.append(("OVER_EXFOLIATE", "CRITICAL: Daily exfoliation can severely damage your skin barrier."))
    elif "Chemically (AHA/BHA) 1-2 times a week" in inputs['exfoliation']:
        category_scores['Routine & Habits'] += 10
    elif "Physically (Scrub) 1-2 times a week" in inputs['exfoliation']:
        category_scores['Routine & Habits'] += 5
        opportunities.append("Physical scrubs can be harsh. Consider switching to a gentle chemical exfoliant (AHA/BHA).")
    elif "Rarely or never" in inputs['exfoliation']:
        category_scores['Routine & Habits'] += 3
        opportunities.append("Gentle exfoliation 1-2 times/week can help with dullness and texture.")

    # 3. Internal Health (Max 30)
    # --- LOGIC UPDATED FOR STRING VALUES ---
    # Sleep (15 pts)
    if inputs['sleep'] == '8+ hours':
        category_scores['Internal Health'] += 15
    elif inputs['sleep'] == '7-8 hours':
        category_scores['Internal Health'] += 12
    elif inputs['sleep'] == '5-6 hours':
        category_scores['Internal Health'] += 7
    else: # 'Less than 5 hours'
        warnings.append(("POOR_SLEEP", "Less than 6 hours of sleep significantly increases cortisol (stress hormone)."))

    # Diet/Water (15 pts)
    if inputs['diet'] == 'Balanced (Mainly whole foods, fruits, veggies)':
        category_scores['Internal Health'] += 8
    else:
        warnings.append(("POOR_DIET", "A high-sugar/processed diet can trigger inflammation and breakouts."))
    
    if inputs['water'] == '8+ glasses':
        category_scores['Internal Health'] += 7
    elif inputs['water'] == '5-7 glasses':
        category_scores['Internal Health'] += 4
    else: # '4 or less glasses'
        opportunities.append("Your skin is likely dehydrated. Increasing water is the easiest way to improve plumpness.")
        
    # Smoking Penalty (applies to total)
    total_penalty = 0
    if inputs['smoking'] == 'Yes, regularly':
        total_penalty = 15 # Full penalty for regular use
        warnings.append(("SMOKING_REGULAR", "CRITICAL: Regular smoking is one of the most damaging factors for skin health. It rapidly accelerates aging and hinders repair."))
    elif inputs['smoking'] == 'Yes, occasionally':
        total_penalty = 7  # A partial, but still significant, penalty
        warnings.append(("SMOKING_OCCASIONAL", "CRITICAL: Even occasional smoking constricts blood vessels, reduces oxygen to the skin, and accelerates aging."))
    # 4. External Factors (Max 15)
    # Stress (10 pts)
    if inputs['stress'] == 'Low (Well-managed)': category_scores['External Factors'] += 10
    elif inputs['stress'] == 'Medium (Comes and goes)': category_scores['External Factors'] += 5
    else: # High
        warnings.append(("HIGH_STRESS", "High stress can weaken your skin barrier and trigger breakouts."))
        
    # Environment (5 pts)
    if inputs['environment'] == 'Rural / Low Pollution': category_scores['External Factors'] += 5
    elif inputs['environment'] == 'Suburban / Medium Pollution': category_scores['External Factors'] += 2
    else: # Urban
        opportunities.append("High pollution creates free radicals. An antioxidant serum (like Vitamin C) is highly recommended.")
    
    # --- Final Calculation ---
    total_score = sum(category_scores.values()) - total_penalty
    total_score = max(0, min(100, total_score)) # Clamp score between 0-100
    
    return total_score, category_scores, max_scores, warnings, opportunities

def get_targeted_advice(profile, warnings):
    """
    Generates a prioritized list of advice based on warnings and inferred goals.
    """
    advice_list = []
    
    # --- Check for CRITICAL barrier issues first ---
    critical_warnings = [w[0] for w in warnings]
    
    if "BARRIER_DAMAGE" in critical_warnings or "OVER_EXFOLIATE" in critical_warnings:
        advice_list.append("PRIORITY #1: STOP ALL ACTIVES. Your skin barrier is likely damaged. For 2 weeks, use ONLY:")
        advice_list.append("1. A gentle, non-foaming cleanser.")
        advice_list.append("2. A simple, 'barrier repair' moisturizer (with Ceramides, Cica, or Squalane).")
        advice_list.append("3. Your daily SPF.")
        return advice_list # Stop here
        
    if "SMOKING" in critical_warnings:
        advice_list.append("PRIORITY #1: No product can reverse the internal damage from smoking. This is the single most impactful factor to address for your skin health.")
        
    if "SUNSCREEN_NONE" in critical_warnings:
        advice_list.append("PRIORITY #2: You MUST start using a Broad-Spectrum SPF 30-50+ every single morning. No other product will be effective without this.")

    if "SLEEP_IN_MAKEUP" in critical_warnings:
        advice_list.append("PRIORITY #3: You must stop sleeping in makeup. Get a gentle oil cleanser or cleansing balm to use *before* your regular cleanser.")
        
    # --- If no critical issues, give targeted advice based on inferred goals ---
    if not advice_list:
        advice_list.append("You have a solid foundation! Here is a targeted plan based on your skin profile:")

    concerns = profile.get('Inferred Concerns', '')
    skin_type = profile.get('Inferred Type', '')
    
    if 'Acne-Prone' in concerns:
        if 'Oily' in skin_type or 'Combination' in skin_type:
            advice_list.append("For YOUR ACNE: Introduce a **Salicylic Acid (BHA)** serum 2-3 times a week at night. It cleans *inside* the pore.")
        else: # Dry
            advice_list.append("For YOUR ACNE (Dry Skin): Try a gentler **Azelaic Acid** or a low-strength **Retinoid** to promote cell turnover without over-drying.")
            
    if 'Redness-Prone' in concerns or profile.get('Inferred Sensitivity') == 'High':
        advice_list.append("For YOUR REDNESS/SENSITIVITY: Look for calming ingredients. **Azelaic Acid**, **Centella Asiatica (Cica)**, **Niacinamide**, and **Oat** are all excellent.")
        
    if 'Dullness' in concerns:
        advice_list.append("For YOUR DULLNESS: Introduce a gentle chemical exfoliant. For dry/sensitive skin, try **Lactic Acid** or **Mandelic Acid**. For oily/normal skin, **Glycolic Acid** is effective. Use 1-2 times a week at night.")
        
    if 'Dry' in skin_type:
        advice_list.append("For YOUR DRYNESS: Look for 'humectants' and 'occlusives'. Apply **Hyaluronic Acid** or **Glycerin** serums to DAMP skin, then 'seal' it in with a moisturizer containing **Ceramides** or **Squalane**.")

    if "General Maintenance" in concerns:
        advice_list.append("For MAINTENANCE: Your goal is protection! A **Vitamin C** serum in the AM (under SPF) and a **Hydrating Serum** (like Hyaluronic Acid) at night is a perfect, simple routine.")

    return advice_list

# --- UI Functions ---

def draw_taskbar():
    """Draws the top navigation taskbar"""
    if 'max_step' not in st.session_state:
        st.session_state.max_step = 1

    current_step_num = st.session_state.step
    if current_step_num == "results":
        current_step_num = 5

    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns(5)
    
    with cols[0]:
        if st.button("Step 1: Profile", use_container_width=True, type=("primary" if current_step_num == 1 else "secondary")):
            st.session_state.step = 1
            st.rerun()
    
    with cols[1]:
        disabled_2 = st.session_state.max_step < 2
        if st.button("Step 2: Lifestyle", use_container_width=True, type=("primary" if current_step_num == 2 else "secondary"), disabled=disabled_2):
            st.session_state.step = 2
            st.rerun()
    
    with cols[2]:
        disabled_3 = st.session_state.max_step < 3
        if st.button("Step 3: Routine", use_container_width=True, type=("primary" if current_step_num == 3 else "secondary"), disabled=disabled_3):
            st.session_state.step = 3
            st.rerun()
    
    with cols[3]:
        disabled_4 = st.session_state.max_step < 4
        if st.button("Step 4: Environment", use_container_width=True, type=("primary" if current_step_num == 4 else "secondary"), disabled=disabled_4):
            st.session_state.step = 4
            st.rerun()

    with cols[4]:
        disabled_5 = st.session_state.max_step < 5
        if st.button("Results", use_container_width=True, type=("primary" if current_step_num == 5 else "secondary"), disabled=disabled_5):
            st.session_state.step = "results"
            st.rerun()
    st.divider()


def step_1_profile():
    draw_taskbar() 
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        # st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("<h2>Step 1: Your Skin Profile</h2>", unsafe_allow_html=True)
        st.write("Let's understand your skin's behavior. Answer these to build your unique profile.")
        
        inputs = {}
        
        # --- WIDGET CHANGED from selectbox to radio ---
        feeling_options = ('Comfortable (not oily or dry)', 'Tight and dry', 'Shiny in the T-zone, dry on cheeks', 'Shiny all over')
        feeling_default = st.session_state.inputs.get('feeling', 'Comfortable (not oily or dry)')
        inputs['feeling'] = st.radio(
            "30 minutes after washing your face (and applying no product), how does it feel?",
            feeling_options,
            index=feeling_options.index(feeling_default)
        )
        st.divider()
        
        breakout_options = ('Rarely', 'Occasionally (e.g., hormonal)', 'Frequently')
        breakout_default = st.session_state.inputs.get('breakouts', 'Rarely')
        inputs['breakouts'] = st.radio(
            "How often do you experience breakouts?",
            breakout_options,
            index=breakout_options.index(breakout_default)
        )
        st.divider()
        
        sensitivity_options = ('Usually fine', 'Sometimes stings or gets red', 'Often breaks out')
        sensitivity_default = st.session_state.inputs.get('sensitivity', 'Usually fine')
        inputs['sensitivity'] = st.radio(
            "How does your skin typically react to new products?",
            sensitivity_options,
            index=sensitivity_options.index(sensitivity_default)
        )
        st.divider()
        
        reactivity_options = ('Mostly clear and even-toned', 'Often red or blotchy', 'Looks dull or has uneven texture')
        reactivity_default = st.session_state.inputs.get('reactivity', 'Mostly clear and even-toned')
        inputs['reactivity'] = st.radio(
            "Which of these best describes your skin's typical appearance?",
            reactivity_options,
            index=reactivity_options.index(reactivity_default)
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Next: Core Lifestyle", type="primary", use_container_width=True):
            st.session_state.inputs.update(inputs)
            st.session_state.step = 2
            st.session_state.max_step = max(st.session_state.max_step, 2)
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

def step_2_lifestyle():
    draw_taskbar() 
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        # st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("<h2>Step 2: Core Lifestyle</h2>", unsafe_allow_html=True)

        inputs = {}
        
        # --- WIDGET CHANGED from slider to select_slider ---
        sleep_options = ('8+ hours', '7-8 hours', '5-6 hours', 'Less than 5 hours')
        sleep_default = st.session_state.inputs.get('sleep', '7-8 hours')
        # Ensure default is valid, else pick first option
        if sleep_default not in sleep_options: sleep_default = sleep_options[0] 
        inputs['sleep'] = st.select_slider(
            "On average, how many hours of sleep do you get per night?",
            options=sleep_options,
            value=sleep_default
        )
        st.divider()

        # --- WIDGET CHANGED from slider to select_slider ---
        water_options = ('8+ glasses', '5-7 glasses', '4 or less glasses')
        water_default = st.session_state.inputs.get('water', '5-7 glasses')
        if water_default not in water_options: water_default = water_options[0]
        inputs['water'] = st.select_slider(
            "How many glasses of water (approx. 8 oz / 250ml) do you drink per day?",
            options=water_options,
            value=water_default
        )
        st.divider()

        # --- WIDGET CHANGED from selectbox to radio ---
        diet_options = ['Balanced (Mainly whole foods, fruits, veggies)', 'Average (A mix of healthy and processed/takeout)', 'High in Sugar, Dairy, or Processed Foods']
        diet_default = st.session_state.inputs.get('diet', 'Average (A mix of healthy and processed/takeout)')
        inputs['diet'] = st.radio(
            "Which best describes your diet?",
            diet_options,
            index=diet_options.index(diet_default)
        )
        st.divider()
        
        smoking_options = ['No, never', 'Yes, occasionally', 'Yes, regularly']
        smoking_default = st.session_state.inputs.get('smoking', 'No, never')
        inputs['smoking'] = st.radio(
            "Do you smoke or vape?",
            smoking_options,
            index=smoking_options.index(smoking_default)
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Next: Daily Routine", type="primary", use_container_width=True):
            st.session_state.inputs.update(inputs)
            st.session_state.step = 3
            st.session_state.max_step = max(st.session_state.max_step, 3)
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

def step_3_routine():
    draw_taskbar() 
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        # st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("<h2>Step 3: Your Daily Routine</h2>", unsafe_allow_html=True)

        inputs = {}
        
        # --- WIDGET CHANGED from selectbox to radio ---
        sunscreen_options = ('Every day, rain or shine, and reapply', 'Most days, when I remember', 'Only on very sunny days', 'Rarely or never')
        sunscreen_default = st.session_state.inputs.get('sunscreen', 'Most days, when I remember')
        inputs['sunscreen'] = st.radio(
            "How often do you apply sunscreen to your face?",
            sunscreen_options,
            index=sunscreen_options.index(sunscreen_default)
        )
        st.divider()
        
        # --- WIDGET CHANGED from selectbox to radio ---
        makeup_options = ('I always double-cleanse (oil/balm first, then cleanser)', 'I use a single, thorough cleanser', 'I primarily use makeup wipes', 'I often forget or sleep in it')
        makeup_default = st.session_state.inputs.get('makeup_removal', 'I use a single, thorough cleanser')
        inputs['makeup_removal'] = st.radio(
            "When you wear makeup/SPF, how do you remove it?",
            makeup_options,
            index=makeup_options.index(makeup_default)
        )
        st.divider()
        
        # --- WIDGET CHANGED from selectbox to radio ---
        exfoliation_options = ('Chemically (AHA/BHA) 1-2 times a week', 'Physically (Scrub) 1-2 times a week', 'Over-exfoliate (Physical scrubs or acids daily)', 'Rarely or never')
        exfoliation_default = st.session_state.inputs.get('exfoliation', 'Rarely or never')
        inputs['exfoliation'] = st.radio(
            "How do you exfoliate?",
            exfoliation_options,
            index=exfoliation_options.index(exfoliation_default)
        )
        st.divider()
        
        st.markdown("<div class='multiselect-label'>Which 'active' ingredients are in your regular routine? (Select all that apply)</div>", unsafe_allow_html=True)
        inputs['actives'] = st.multiselect(
            "Which 'active' ingredients are in your regular routine? (Select all that apply)",
            ['Vitamin C', 'Retinol / Retinoids', 'AHA (Glycolic, Lactic)', 'BHA (Salicylic Acid)', 'Niacinamide', 'Benzoyl Peroxide', 'I use too many things!'],
            default=st.session_state.inputs.get('actives', []),
            label_visibility="collapsed"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Next: Environment", type="primary", use_container_width=True):
            st.session_state.inputs.update(inputs)
            st.session_state.step = 4
            st.session_state.max_step = max(st.session_state.max_step, 4)
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

def step_4_environment():
    draw_taskbar()
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        # st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("<h2>Step 4: Your Environment</h2>", unsafe_allow_html=True)
        
        inputs = {}
        
        # --- WIDGET CHANGED from selectbox to radio ---
        stress_options = ('Low (Well-managed)', 'Medium (Comes and goes)', 'High (Constant)')
        stress_default = st.session_state.inputs.get('stress', 'Medium (Comes and goes)')
        inputs['stress'] = st.radio(
            "How would you rate your average daily stress level?",
            stress_options,
            index=stress_options.index(stress_default)
        )
        st.divider()
        
        # --- WIDGET CHANGED from selectbox to radio ---
        env_options = ('Rural / Low Pollution', 'Suburban / Medium Pollution', 'Urban / High Pollution')
        env_default = st.session_state.inputs.get('environment', 'Suburban / Medium Pollution')
        inputs['environment'] = st.radio(
            "Which best describes your living environment?",
            env_options,
            index=env_options.index(env_default)
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Analyze My Skin!", type="primary", use_container_width=True):
            st.session_state.inputs.update(inputs)
            st.session_state.step = "results"
            st.session_state.max_step = max(st.session_state.max_step, 5)
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

def show_results():
    draw_taskbar() 
    st.markdown("<h1>Your Skin Analysis Results</h1>", unsafe_allow_html=True)
    
    inputs = st.session_state.inputs
    
    # Check if all inputs are present, if not, send back to step 1
    required_keys = ['feeling', 'sleep', 'sunscreen', 'stress'] # Just a sample
    if not all(key in inputs for key in required_keys):
        st.error("It seems you missed some questions. Please start over.")
        if st.button("Start Over", type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        return

    profile = analyze_profile(inputs)
    total_score, category_scores, max_scores, warnings, opportunities = calculate_score_and_profile(inputs, profile)
    advice = get_targeted_advice(profile, warnings)
    
    # --- Layout for Results ---
    
    col1, col2 = st.columns(2)
    
    with col1:
        # st.markdown('<div class="card-container" style="height: 100%;">', unsafe_allow_html=True)
        st.markdown("<h3>Your Final Score</h3>", unsafe_allow_html=True)
        st.markdown(f'<div class="score-display">{total_score}/100</div>', unsafe_allow_html=True)
        st.progress(total_score / 100.0)
        
        st.markdown("<h3>Your Inferred Profile</h3>", unsafe_allow_html=True)
        st.info(f"""
        * **Skin Type:** {profile.get('Inferred Type')}
        * **Sensitivity:** {profile.get('Inferred Sensitivity')}
        * **Primary Concerns:** {profile.get('Inferred Concerns')}
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # st.markdown('<div class="card-container" style="height: 100%;">', unsafe_allow_html=True)
        st.markdown("<h3>Your Skin Health Shape</h3>", unsafe_allow_html=True)
        
        # --- Radar Chart ---
        categories = list(max_scores.keys())
        normalized_scores = [category_scores[cat] / max_scores[cat] for cat in categories]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=normalized_scores + [normalized_scores[0]], # Add first point to end to close the shape
            theta=categories + [categories[0]], # Add first category to end
            fill='toself',
            name='Your Score',
            line=dict(color='#957DAD'), 
            fillcolor='rgba(149, 125, 173, 0.3)'
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1], color="#6D617A", gridcolor="rgba(109, 97, 122, 0.2)"),
                angularaxis=dict(color="#4A3F5E", gridcolor="rgba(109, 97, 122, 0.2)")
            ),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Montserrat, sans-serif", color="#4A3F5E")
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    
    # st.markdown('<div class="card-container">', unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Your Prioritized Action Plan")
        st.info("This advice is prioritized. Focus on #1 first.")
        for i, item in enumerate(advice, 1):
            st.markdown(f"**{i}.** {item}")
            
        st.subheader("💡 Opportunities")
        if opportunities:
            st.warning("These are small tweaks that can boost your score and overall skin health.")
            for text in opportunities:
                st.markdown(f"- {text}")
        else:
            st.success("You're already optimizing in all key areas!")

    with col4:
        st.subheader("🚨 Critical Warnings")
        if warnings:
            st.error("Address these issues immediately. They are actively harming your skin health.")
            for code, text in warnings:
                st.markdown(f"- {text}")
        else:
            st.success("Great job! You have no critical habits that are actively harming your skin.")

        st.subheader("Score Breakdown")
        # --- Bar Chart ---
        categories = list(max_scores.keys())
        data = {
            "Category": categories,
            "Your Score": list(category_scores.values()),
            "Max Possible": list(max_scores.values()),
        }
        df_bar = pd.DataFrame(data).melt('Category', var_name='Score Type', value_name='Points')

        # Use a grouped bar chart (no faceting) so the chart stays within the container width
        # and doesn't produce a long horizontal scroll. We use xOffset to dodge bars by Score Type.
        bar_chart = alt.Chart(df_bar).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X('Category:N', title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Points:Q', title="Score"),
            color=alt.Color('Score Type:N', title="", scale={"range": ["#957DAD", "#EAE6F0"]}),
            xOffset='Score Type:N',
            tooltip=['Category', 'Score Type', 'Points']
        ).properties(
            title="Your Score vs. Possible Score"
        ).configure_view(
            strokeWidth=0
        )

        st.altair_chart(bar_chart, use_container_width=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    if st.button("Start Over", type="primary", use_container_width=True):
        # Clear all session state keys to reset the app
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- MAIN APP LOGIC ---

st.set_page_config(layout="wide")
load_css() # Load the theme
st.markdown("""
<div style="text-align:center; margin-top:0.5rem; margin-bottom:1.25rem;">
    <div style="font-family: 'Lora', serif; color:#957DAD; font-weight:650; letter-spacing:4px; text-transform:uppercase;
                font-size:clamp(1.0rem, 3.5vw, 2.3rem); text-shadow: 0 6px 20px rgba(149,125,173,0.25);">
        DermacScribe
    </div>
    <div style="font-family: 'Lora', serif; color:#4A3F5E; font-weight:650; letter-spacing:1px;
                font-size:clamp(2.2rem, 6.1vw, 3.8rem); margin-top:0.3rem; text-shadow: 0 8px 30px rgba(74,63,94,0.08);">
        Pro Skin Analyzer
    </div>
</div>
""", unsafe_allow_html=True)


# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
    st.session_state.inputs = {}
    st.session_state.max_step = 1 # NEW

# Step navigation
if st.session_state.step == 1:
    step_1_profile()
elif st.session_state.step == 2:
    step_2_lifestyle()
elif st.session_state.step == 3:
    step_3_routine()
elif st.session_state.step == 4:
    step_4_environment()
elif st.session_state.step == "results":
    # Show a classy heading (replace the previous playful title) with a superheading "DERMASCRIBE"
    # st.markdown("""
    # <div style="text-align:center; margin-bottom: 1rem;">
    #     <div style="font-family: 'Lora', serif; color:#957DAD; font-weight:700; letter-spacing:3px; font-size:0.9rem;">
    #         DERMASCRIBE
    #     </div>
    #     <div style="font-family: 'Lora', serif; color:#4A3F5E; font-weight:700; font-size:2rem;">
    #         The Skin Health Advisor
    #     </div>
    # </div>
    # """, unsafe_allow_html=True)

    show_results()