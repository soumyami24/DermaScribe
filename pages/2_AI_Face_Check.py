import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import json
import ast  # Using ast.literal_eval for safe parsing of AI-generated lists

# --- Configuration ---

# Set page config (from testui.py)
st.set_page_config(layout="wide", page_title="DermacScribe", page_icon="✨")

# --- Version-aware rerun import ---
try:
    from streamlit import rerun as st_rerun
except ImportError:
    from streamlit import experimental_rerun as st_rerun

# Configure Gemini API
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"Failed to configure Gemini API. Make sure your GEMINI_API_KEY is in Streamlit secrets. Error: {e}")
    st.stop()

# --- AI Models ---
vision_model = genai.GenerativeModel('gemini-2.5-flash')
text_model = genai.GenerativeModel('gemini-2.5-flash')

# --- Prompts ---
IMAGE_ANALYSIS_PROMPT = """
You are a dermatology assistant. Analyze the provided image(s) of a person's face.
Your ONLY task is to identify and list visible skin concerns.
- If you see a clear face, return a Python-compatible list of strings, e.g., ["Redness on cheeks", "Forehead acne", "Dark circles"].
- If no face is detected, return the exact string: ["NO_FACE_DETECTED"]
- If the image is too blurry, dark, or unclear to analyze, return the exact string: ["UNABLE_TO_ANALYZE_UNCLEAR"]
- Do not add any other text, explanation, or greeting.
"""

QUESTION_GENERATION_PROMPT_TEMPLATE = """
Based on the following detected skin concerns, generate 3-5 simple follow-up questions for the user.
These questions should help gather more context about their lifestyle, habits, and feelings (e.g., itchy, oily, dry).
Return a Python-compatible list of strings.

Detected concerns: {concerns}

Example output:
[
    "Does your skin feel tight or dry after washing?",
    "Do the red areas feel itchy or hot?",
    "What is your current daily skincare routine?"
]
"""

# --- JSON Schema for Final Analysis ---
FINAL_ANALYSIS_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "skin_score": {"type": "INTEGER", "description": "Overall skin score from 0-100."},
        "skin_age": {"type": "INTEGER", "description": "Estimated skin age."},
        "graphic_analysis": {
            "type": "ARRAY",
            "description": "A list of scores for different skin metrics.",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "name": {"type": "STRING", "description": "Name of the metric (e.g., Skin Radiance, Skin Uniformness)."},
                    "score": {"type": "INTEGER", "description": "Score for this metric (0-100, or ITA score)."},
                    "is_ita": {"type": "BOOLEAN", "description": "True if this is an ITA score (which can be negative)."}
                },
                "required": ["name", "score"]
            }
        },
        "recommendations": {
            "type": "ARRAY",
            "description": "List of recommendations for each detected concern.",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "concern": {"type": "STRING", "description": "The skin concern being addressed (e.g., Redness on cheeks)."},
                    "analysis": {"type": "STRING", "description": "AI's detailed explanation of this concern for the user."},
                    "products": {
                        "type": "ARRAY",
                        "description": "Two product suggestions for this concern.",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "type": {"type": "STRING", "description": "Product category (e.g., Calming Serum, Gentle Moisturizer)."},
                                "ingredients": {"type": "STRING", "description": "Key ingredients to look for (e.g., Niacinamide, Ceramides)."},
                                "examples": {"type": "STRING", "description": "Popular product examples (e.g., The Ordinary Niacinamide 10%)."}
                            },
                            "required": ["type", "ingredients", "examples"]
                        }
                    }
                },
                "required": ["concern", "analysis", "products"]
            }
        },
        "final_tips": {
            "type": "ARRAY",
            "description": "A list of general, actionable tips.",
            "items": {"type": "STRING"}
        }
    },
    "required": ["skin_score", "skin_age", "graphic_analysis", "recommendations", "final_tips"]
}

# --- NEW STYLING (from testui.py) ---
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
        text-align: center; /* <<< ALIGNMENT STYLES */
    }
    h1 { font-size: 3.5rem; } 
    h2 { font-size: 2.5rem; margin-bottom: 2rem; } 
    h3 { font-size: 1.8rem; }
    
    p, li {
        font-size: 1.1rem;
        color: var(--color-text-medium);
    }

    /* --- Base Card (from testui.py) --- */
    .card-container { 
        background-color: var(--color-bg-card); 
        border-radius: 20px; 
        padding: 2.5rem; 
        border: 1px solid var(--color-border); 
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05); 
    }
    
    /* Center-aligned card for home page */
    .content-card {
        background-color: var(--color-bg-card);
        border-radius: 20px;
        padding: 2.5rem;
        border: 1px solid var(--color-border);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        text-align: center;
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
        width: 100%; /* Make buttons full width inside containers */
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
    
    /* --- Style info/warning/error boxes --- */
    .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .stAlert[data-baseweb="alert"] {
        background-color: #F6F4FF; /* Light purple */
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
    
    /* --- STYLES MERGED FROM recom.py (and re-themed) --- */

    /* Circular progress bar */
    .progress-circle-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 20px;
    }
    .progress-circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        /* UPDATED COLOR */
        background: conic-gradient(
            var(--color-accent-purple) {progress_percentage}%, 
            var(--color-border) 0
        );
        font-size: 24px;
        font-weight: bold;
        color: var(--color-text-dark);
        position: relative;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .progress-circle-inner {
        width: 100px;
        height: 100px;
        background: var(--color-bg-card); /* White */
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .progress-circle-label {
        margin-top: 10px;
        font-size: 16px;
        font-weight: 500;
        color: var(--color-text-medium);
        text-align: center;
    }

    /* Recommendation card styling */
    .recommendation-card {
        background-color: var(--color-bg-card); /* White */
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        /* UPDATED BORDER COLOR */
        border-left: 5px solid var(--color-accent-purple);
        text-align: left; /* Keep card text left-aligned */
    }
    .recommendation-card h3 {
        /* UPDATED COLORS */
        color: var(--color-accent-purple);
        border-bottom: 2px solid var(--color-border);
        padding-bottom: 8px;
        text-align: left; /* Keep card headings left-aligned */
    }

    /* Product card styling */
    .product-card {
        /* UPDATED COLORS */
        background-color: var(--color-bg-light); /* Soft Off-White */
        border: 1px solid var(--color-border);
        border-radius: 8px;
        padding: 16px;
        margin-top: 12px;
    }
    .product-card-title {
        font-weight: bold;
        font-size: 1.1em;
        /* UPDATED COLOR */
        color: var(--color-text-dark);
    }

</style>
""", unsafe_allow_html=True)

# --- Global Title (from testui.py) ---
st.markdown("""
<div style="text-align:center; margin-top:0.5rem; margin-bottom:1.25rem;">
    <div style="font-family: 'Lora', serif; color:#957DAD; font-weight:650; letter-spacing:4px; text-transform:uppercase;
                font-size:clamp(1.0rem, 3.5vw, 2.3rem); text-shadow: 0 6px 20px rgba(149,125,173,0.25);">
        DermacScribe
    </div>
    <div style="font-family: 'Lora', serif; color:#4A3F5E; font-weight:650; letter-spacing:1px;
                font-size:clamp(2.2rem, 6.1vw, 3.8rem); margin-top:0.3rem; text-shadow: 0 8px 30px rgba(74,63,94,0.08);">
        AI Face Check
    </div>
</div>
""", unsafe_allow_html=True)


# --- Helper Functions (No UI changes needed) ---

def safe_parse_list(response_text):
    """Safely parse AI response that should be a list."""
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        try:
            parsed = ast.literal_eval(response_text)
            if isinstance(parsed, list):
                return parsed
            else:
                return None
        except (ValueError, SyntaxError):
            return None

def call_gemini_vision(images_bytes_list):
    """First AI call: Analyzes images to detect concerns."""
    prompt_parts = [IMAGE_ANALYSIS_PROMPT]
    image_parts = []
    for img_bytes in images_bytes_list:
        try:
            img = Image.open(io.BytesIO(img_bytes))
            image_parts.append(img)
        except Exception as e:
            st.warning(f"Could not process an image: {e}")
            continue
    if not image_parts:
        return ["UNABLE_TO_ANALYZE_UNCLEAR"]
    prompt_parts.extend(image_parts)
    try:
        response = vision_model.generate_content(prompt_parts)
        parsed_list = safe_parse_list(response.text)
        if parsed_list and isinstance(parsed_list, list):
            return parsed_list
        else:
            return ["UNABLE_TO_ANALYZE_UNCLEAR"]
    except Exception as e:
        st.error(f"An error occurred during image analysis: {e}")
        return ["UNABLE_TO_ANALYZE_UNCLEAR"]

def call_gemini_questions(concerns):
    """Second AI call: Generates follow-up questions."""
    prompt = QUESTION_GENERATION_PROMPT_TEMPLATE.format(concerns=", ".join(concerns))
    try:
        response = text_model.generate_content(prompt)
        parsed_list = safe_parse_list(response.text)
        if parsed_list and isinstance(parsed_list, list):
            return parsed_list
        else:
            return ["No follow-up questions could be generated. Proceeding with analysis."]
    except Exception as e:
        st.error(f"An error occurred while generating questions: {e}")
        return ["An error occurred. Proceeding with analysis."]

def call_gemini_final_analysis(images_bytes_list, concerns, questions, answers):
    """Third AI call: Generates the final, structured analysis."""
    prompt_lines = [
        "You are DermacScribe, an expert AI dermatology advisor. You will receive a user's skin images, a list of concerns you detected, questions you asked, and the user's answers.",
        "Your task is to provide a complete, kind, and actionable skin analysis.",
        "Return your analysis ONLY in the provided JSON format.",
        "\n--- DETECTED CONCERNS ---", "\n".join(f"- {c}" for c in concerns),
        "\n--- QUESTIONS ASKED ---", "\n".join(f"- {q}" for q in questions),
        "\n--- USER'S ANSWERS ---", "\n".join(f"- {a}" for a in answers),
        "\n--- ANALYSIS REQUEST ---",
        "Based on all this information (including the images), generate the final report. Be empathetic and detailed in your 'analysis' text for each concern. Ensure product examples are popular and real.",
        "Here are the images:"
    ]
    image_parts = []
    for img_bytes in images_bytes_list:
        try:
            img = Image.open(io.BytesIO(img_bytes))
            image_parts.append(img)
        except Exception:
            continue
    prompt_parts = prompt_lines + image_parts
    try:
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=FINAL_ANALYSIS_SCHEMA
        )
        response = text_model.generate_content(
            prompt_parts,
            generation_config=generation_config
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"A critical error occurred during the final analysis: {e}")
        print(f"Final analysis error: {e}")
        return {
            "skin_score": 0, "skin_age": 0, "graphic_analysis": [],
            "recommendations": [{"concern": "Error", "analysis": "Could not generate analysis.", "products": []}],
            "final_tips": ["Please try again. An error occurred."]
        }

# --- UI Rendering Functions (NOW RE-STYLED) ---

def render_home():
    """Renders the home page (Step 0 & 1) with new layout."""
    
    # Use centered column layout from testui.py
    _ , col_center, _ = st.columns([1, 4, 1]) # 1:4:1 ratio for wider center
    
    with col_center:
        st.markdown("<h2>Welcome to Your AI Face Check</h2>", unsafe_allow_html=True)
        st.markdown(
            "<p style='text-align: center; font-size: 1.2rem; margin-bottom: 2rem;'>Get personalized, actionable advice by analyzing your skin concerns.</p>", 
            unsafe_allow_html=True
        )
        
        # st.markdown('<div class="content-card">', unsafe_allow_html=True)
        
        main_option = st.radio(
            "How would you like to start?",
            ("Scan Face with Image", "Describe Your Concern"),
            horizontal=True,
            key="main_option",
            label_visibility="collapsed" # Hide label, title is above
        )
        
        st.divider()

        if main_option == "Scan Face with Image":
            st.session_state.page = "image_upload"
            
            image_option = st.radio(
                "Choose your image source:",
                ("Upload an Image", "Use Live Camera"),
                key="image_option"
            )
            
            uploaded_images_bytes = []
            
            if image_option == "Upload an Image":
                uploaded_file = st.file_uploader(
                    "Upload a clear, well-lit photo of your face (JPG, PNG).",
                    type=["jpg", "png", "jpeg"]
                )
                if uploaded_file:
                    uploaded_images_bytes = [uploaded_file.getvalue()]
            
            else: # Use Live Camera
                st.info("Please provide three clear photos for a complete analysis.")
                img_left = st.camera_input("1. Left Profile")
                img_center = st.camera_input("2. Center Face")
                img_right = st.camera_input("3. Right Profile")
                
                if img_left and img_center and img_right:
                    uploaded_images_bytes = [
                        img_left.getvalue(),
                        img_center.getvalue(),
                        img_right.getvalue()
                    ]

            st.markdown("<br>", unsafe_allow_html=True)
            # Analyze button (full width by default from new CSS)
            if st.button("Analyze Image(s)", type="primary", disabled=not uploaded_images_bytes):
                with st.spinner("Analyzing your image(s)... This is the first step."):
                    st.session_state.uploaded_images = uploaded_images_bytes
                    detected_concerns = call_gemini_vision(uploaded_images_bytes)
                    
                    if not detected_concerns or not isinstance(detected_concerns, list):
                        st.error("I couldn't analyze that image. It might be unclear or not contain a face. Please try again.")
                        st.session_state.page = "home"
                    elif detected_concerns == ["NO_FACE_DETECTED"]:
                        st.error("No face was detected in the image. Please upload a clear photo of your face.")
                        st.session_state.page = "home"
                    elif detected_concerns == ["UNABLE_TO_ANALYZE_UNCLEAR"]:
                        st.error("I couldn't analyze that image. It might be too blurry or dark. Please try a different one.")
                        st.session_state.page = "home"
                    else:
                        st.session_state.detected_concerns = detected_concerns
                        st.session_state.page = "analysis_questions"
                        st_rerun()

        else: # Describe Your Concern
            st.session_state.page = "text_analysis"
            st_rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)


def render_question_page():
    """Renders the follow-up question form with new layout."""
    
    _ , col_center, _ = st.columns([1, 4, 1])
    
    with col_center:
        st.markdown("<h2>Just a few more details...</h2>", unsafe_allow_html=True)
        st.markdown(
            "<p style='text-align: center; font-size: 1.2rem;'>This will help me give you a more accurate analysis.</p>", 
            unsafe_allow_html=True
        )
        
        if "generated_questions" not in st.session_state:
            with st.spinner("Generating personalized questions..."):
                st.session_state.generated_questions = call_gemini_questions(st.session_state.detected_concerns)
        
        st.markdown("<h3>Here's what I detected:</h3>", unsafe_allow_html=True)
        # .stAlert CSS will automatically style st.info
        for concern in st.session_state.detected_concerns:
            st.info(f"• {concern}")
        
        st.divider()
        
        st.markdown("<h3>Please answer these questions:</h3>", unsafe_allow_html=True)
        with st.form(key="qa_form"):
            user_answers = []
            questions = st.session_state.generated_questions
            
            for i, question in enumerate(questions):
                answer = st.text_input(question, key=f"q_{i}")
                user_answers.append(f"Q: {question}\nA: {answer}")
                
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Get My Full Analysis", type="primary")
            
            if submitted:
                st.session_state.user_answers = user_answers
                st.session_state.page = "results"
                st_rerun()


def render_results_page():
    """Renders the final analysis with new styles."""
    
    if "final_analysis" not in st.session_state:
        with st.spinner("Compiling your complete analysis... This may take a moment."):
            st.session_state.final_analysis = call_gemini_final_analysis(
                st.session_state.uploaded_images,
                st.session_state.detected_concerns,
                st.session_state.generated_questions,
                st.session_state.user_answers
            )

    analysis = st.session_state.final_analysis
    
    # Use centered column for the main content
    _ , col_center, _ = st.columns([1, 6, 1]) # Wider center for results
    with col_center:
        # --- Header ---
        st.markdown("<h1>Your Complete Skin Analysis is Ready!</h1>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Estimated Skin Age", analysis.get('skin_age', 'N/A'))
        with col2:
            st.metric("Overall Skin Score", f"{analysis.get('skin_score', 'N/A')}/100")
            
        st.divider()
        
        # --- Graphic Analysis ---
        st.markdown("<h2>Your Scoring Breakdown</h2>", unsafe_allow_html=True)
        st.markdown(
            "<p style='text-align: center; font-size: 1.1rem;'>Here's how your skin metrics look.</p>", 
            unsafe_allow_html=True
        )
        
        graphic_data = analysis.get('graphic_analysis', [])
        if graphic_data:
            # Create 4 columns for the graphic layout
            cols = st.columns(4)
            col_index = 0
            for item in graphic_data:
                score = item.get('score', 0)
                name = item.get('name', 'Metric')
                is_ita = item.get('is_ita', False)
                
                progress_percentage = score
                if is_ita:
                    display_score = str(score)
                    progress_percentage = 0
                else:
                    display_score = f"{score}%"
                    progress_percentage = max(0, min(100, score))

                with cols[col_index % 4]:
                    # The CSS for this is now in the main <style> block
                    progress_circle_html = f"""
                    <div class="progress-circle-container">
                        <div class="progress-circle" style="background: conic-gradient(var(--color-accent-purple) {progress_percentage}%, var(--color-border) 0);">
                            <div class="progress-circle-inner">
                                <span>{display_score}</span>
                            </div>
                        </div>
                        <div class="progress-circle-label">{name}</div>
                    </div>
                    """
                    st.markdown(progress_circle_html, unsafe_allow_html=True)
                
                col_index += 1
        else:
            st.info("No graphical analysis data was returned.")

        st.divider()

        # --- Actionable Recommendations ---
        st.markdown("<h2>Actionable Recommendations</h2>", unsafe_allow_html=True)
        
        recommendations = analysis.get('recommendations', [])
        if not recommendations:
            st.warning("No specific recommendations were generated.")
            
        for item in recommendations:
            # The CSS for this is now in the main <style> block
            st.markdown('<div class="recommendation-card">', unsafe_allow_html=True)
            st.subheader(f"Concern: {item.get('concern', 'N/A')}")
            
            st.markdown("#### AI Analysis")
            st.markdown(item.get('analysis', 'No analysis provided.'))
            
            st.markdown("#### Product Suggestions")
            prod_cols = st.columns(2)
            products = item.get('products', [])
            
            for i, prod in enumerate(products):
                with prod_cols[i % 2]:
                    st.markdown('<div class="product-card">', unsafe_allow_html=True)
                    st.markdown(f"<span class='product-card-title'>{prod.get('type', 'Product')}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Key Ingredients:** {prod.get('ingredients', 'N/A')}")
                    st.markdown(f"**Examples:** {prod.get('examples', 'N/A')}")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            if not products:
                st.markdown("<p>No specific products suggested for this concern.</p>", unsafe_allow_html=True)
                
            # st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # --- Final Tips ---
        st.markdown("<h2>Final Tips from Your AI Advisor</h2>", unsafe_allow_html=True)
        final_tips = analysis.get('final_tips', [])
        for tip in final_tips:
            # .stAlert CSS will automatically style st.success
            st.success(f"💡 {tip}")
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Start Over", type="primary"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st_rerun()


def render_text_analysis():
    """Placeholder for the simple text-based analysis flow."""
    
    _ , col_center, _ = st.columns([1, 4, 1])
    with col_center:
        st.markdown("<h2>Describe Your Concern</h2>", unsafe_allow_html=True)
        st.markdown(
            "<p style='text-align: center; font-size: 1.1rem;'>Tell us about your main skin concerns, your skin type, and your current routine.</p>", 
            unsafe_allow_html=True
        )
        
        with st.form("text_analysis_form"):
            user_description = st.text_area("Your skin concerns:", height=200, label_visibility="collapsed")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Get Advice", type="primary")
            
            if submitted and user_description:
                with st.spinner("Analyzing your description..."):
                    prompt = f"""
                    A user has described their skin concern. Act as an AI dermatology assistant and provide a simple, actionable skincare routine.
                    Format your response in Markdown.
                    Focus on product types (e.g., gentle cleanser, moisturizer, sunscreen) and key ingredients. Keep it concise and friendly.
                    
                    USER'S DESCRIPTION:
                    "{user_description}"
                    
                    YOUR ADVICE:
                    """
                    try:
                        response = text_model.generate_content(prompt)
                        st.markdown("---")
                        st.markdown("<h3>Here's some advice based on your description:</h3>", unsafe_allow_html=True)
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"An error occurred: {e}")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Go Back Home", type="secondary"): # Use secondary style
            st.session_state.page = "home"
            st_rerun()


# --- Main App Logic (Router) ---

if "page" not in st.session_state:
    st.session_state.page = "home"

if st.session_state.page == "home":
    render_home()
elif st.session_state.page == "image_upload":
    render_home()
elif st.session_state.page == "analysis_questions":
    render_question_page()
elif st.session_state.page == "results":
    render_results_page()
elif st.session_state.page == "text_analysis":
    render_text_analysis()