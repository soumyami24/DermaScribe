# weather.py
import streamlit as st
import requests
from datetime import datetime
from streamlit_js_eval import get_geolocation
from PIL import Image
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Skin Health Advisor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- AURORA GLOW STYLING (UX IMPROVEMENTS) ---
def load_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;600;700&family=Montserrat:wght@300;400;500;600&display=swap');

        :root {
            --color-bg-light: #FDFBFF;
            --color-bg-card: #FFFFFF;
            --color-text-dark: #4A3F5E;
            --color-text-medium: #6D617A;
            --color-accent-purple: #957DAD;
            --color-gradient-start: #FFD1DC; /* Light Pink */
            --color-gradient-end: #E0BBE4;   /* Light Violet */
            --color-border: #EAE6F0;
            --font-heading: 'Lora', serif;
            --font-body: 'Montserrat', sans-serif;
            --gradient-main: linear-gradient(135deg, var(--color-gradient-start) 0%, var(--color-gradient-end) 100%);
            --color-shadow: rgba(0, 0, 0, 0.08);
            --color-highlight-bg: #FAF7FF; /* Very light purple for visual contrast */
        }

        html, body, .stApp {
            font-family: var(--font-body);
            color: var(--color-text-medium);
            background-color: var(--color-bg-light);
        }
        /* >>> ADJUSTED HERE: Increased content width by reducing horizontal padding from 5rem to 3rem <<< */
        .main .block-container {
            padding: 2rem 3rem 5rem 3rem; 
        }
        header, footer { visibility: hidden; height: 0px !important; }
        h1, h2, h3, h4, h5, h6 {
            font-family: var(--font-heading);
            color: var(--color-text-dark);
            font-weight: 700; /* Bolder headings */
        }
        h1 { font-size: 3.2rem; }
        h2 { font-size: 2.3rem; margin-bottom: 2rem;}
        h3 { font-size: 1.7rem; }
        p, li { font-size: 1.0rem; color: var(--color-text-medium); line-height: 1.6; }

        .card-container {
            background-color: var(--color-bg-card);
            border-radius: 20px;
            padding: 2.5rem;
            border: 1px solid var(--color-border);
            box-shadow: 0 15px 40px var(--color-shadow); /* Stronger shadow */
            margin-bottom: 2rem;
        }

        /* Button Styling is already good */
        .stButton > button {
            font-family: var(--font-body); font-weight: 600; padding: 0.8rem 1.5rem;
            border-radius: 30px; border: none; transition: all 0.3s ease;
            text-transform: uppercase; letter-spacing: 0.5px;
        }
        .stButton > button:not([kind="secondary"]) {
            background: var(--gradient-main); color: var(--color-text-dark);
            box-shadow: 0 4px 15px rgba(149, 125, 173, 0.3);
        }

        /* Metric Styling: Highlighted Container */
        div[data-testid="stMetric"] {
            background-color: var(--color-highlight-bg); /* Use highlight color */
            border: 1px solid var(--color-accent-purple); /* Accent border */
            border-radius: 15px; 
            padding: 1rem 0.5rem; /* Reduced horizontal padding for metrics only to fit 5 columns better */
            text-align: center; 
            height: 100%;
            box-shadow: 0 5px 15px rgba(149, 125, 173, 0.1); /* Light glow */
        }
         div[data-testid="stMetric"] label {
             font-family: var(--font-body); font-weight: 600; color: var(--color-text-dark); /* Darker label */
             /* Removed white-space: nowrap; to allow titles to wrap slightly if necessary */
             overflow: hidden; text-overflow: ellipsis;
             font-size: 0.95rem; 
         }
         div[data-testid="stMetric"] .st-emotion-cache-1Uddkav { /* Value - Using the common Streamlit class name */
              font-family: var(--font-heading); font-size: 2.2rem; /* Slightly larger value */
              font-weight: 700; color: var(--color-text-dark);
         }
         div[data-testid="stMetricDelta"] { /* Delta text */
              font-family: var(--font-body); font-weight: 600; font-size: 0.95rem; /* Darker/bolder delta */
         }

        /* Advice Card Styling: New Look for visual appeal */
        .advice-card {
            background-color: var(--color-bg-card); 
            border-radius: 15px; 
            padding: 1.5rem 2rem;
            border-left: 5px solid var(--color-accent-purple); /* Strong emphasis line */
            border-bottom: 1px solid var(--color-border);
            margin-bottom: 1.5rem; 
            box-shadow: 0 5px 15px var(--color-shadow);
        }
        .advice-card h3 { 
            font-size: 1.4rem; 
            margin-top: 0; 
            margin-bottom: 0.5rem; /* Reduced space after title */
            display: flex;
            align-items: center;
        }
        .advice-card h3 span.icon { 
            font-size: 1.5em; 
            margin-right: 10px; 
            color: var(--color-accent-purple);
        }
        .advice-card p, .advice-card li { 
            font-size: 0.95rem; 
        }

        /* Expander Styling is already excellent */
        div[data-testid="stExpander"] {
             background-color: var(--color-bg-card) !important; border: 1px solid var(--color-border) !important;
             border-radius: 15px !important; box-shadow: 0 5px 15px rgba(0,0,0,0.03) !important;
             margin-bottom: 1rem !important; transition: box-shadow 0.2s ease;
        }
        div[data-testid="stExpander"] summary p {
              font-family: var(--font-heading) !important; font-weight: 600 !important; font-size: 1.15rem !important;
              color: var(--color-text-dark) !important; transition: color 0.2s ease !important;
        }
        
    </style>
    """, unsafe_allow_html=True)

# --- IMAGE LOADING ---
image_path = os.path.join("C:", os.sep, "Users", "soumy", "OneDrive", "ASUS", "Downloads", "Python-Streamlit", "lavender-themed-skincare-beauty-products-arranged-beautifully-flowers-pastel-packaging-creating-calm-soothing-aesthetic-323793872.webp")
@st.cache_data
def load_local_image(path):
    if not os.path.exists(path):
        st.markdown(f'<div class="custom-alert custom-error">Error: Image file not found at the specified path: {path}</div>', unsafe_allow_html=True)
        return None
    try:
        return Image.open(path)
    except Exception as e:
        st.markdown(f'<div class="custom-alert custom-error">Error loading image: {e}</div>', unsafe_allow_html=True)
        return None
hero_image = load_local_image(image_path)

# --- API Functions (Unchanged) ---
def get_coordinates(location, api_key):
    geo_url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {"q": location, "limit": 1, "appid": api_key}
    try:
        response = requests.get(geo_url, params=params)
        response.raise_for_status()
        data = response.json()
        if not data: return None, None, "City not found."
        return data[0]['lat'], data[0]['lon'], None
    except requests.exceptions.RequestException as e: return None, None, f"API error: {e}"

def get_weather_data(lat, lon, api_key):
    weather_url = "https://api.openweathermap.org/data/2.5/weather"
    uv_url = "https://api.openweathermap.org/data/2.5/uvi"
    aqi_url = "http://api.openweathermap.org/data/2.5/air_pollution"
    weather_params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
    uv_params = {"lat": lat, "lon": lon, "appid": api_key}
    aqi_params = {"lat": lat, "lon": lon, "appid": api_key}
    try:
        weather_r = requests.get(weather_url, params=weather_params); weather_r.raise_for_status(); weather_d = weather_r.json()
        uv_r = requests.get(uv_url, params=uv_params); uv_r.raise_for_status(); uv_d = uv_r.json()
        aqi_r = requests.get(aqi_url, params=aqi_params); aqi_r.raise_for_status(); aqi_d = aqi_r.json()
        return {
            "temp": weather_d['main']['temp'], "humidity": weather_d['main']['humidity'],
            "description": weather_d['weather'][0]['description'], "uv": uv_d['value'],
            "wind_speed": weather_d['wind']['speed'], "aqi": aqi_d['list'][0]['main']['aqi'], "error": None
        }
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401: return {"error": "Invalid API key."}
        return {"error": f"API error: {e}"}
    except requests.exceptions.RequestException as e: return {"error": f"Network error: {e}"}

# --- Skincare Logic Functions (Unchanged) ---
def get_uv_advice(uv, skin_type):
    advice = ""; level = ""
    icon = "☀️"
    if uv <= 2: level = "Low (0-2)"; advice = "**Minimal protection needed.**"; icon = "✅"
    elif uv <= 5: level = "Moderate (3-5)"; advice = "**Protection necessary.** Use broad-spectrum SPF 30+."; icon = "🌥️"
    elif uv <= 7: level = "High (6-7)"; advice = "**High protection required!** SPF 30-50+, seek shade 10am-4pm."; icon = "🌤️"
    elif uv <= 10: level = "Very High (8-10)"; advice = "**Extra protection crucial!** SPF 50+. Limit sun."; icon = "☀️"
    else: level = "Extreme (11+)"; advice = "**Extreme risk!** Stay indoors peak hours. SPF 50+, clothes, shade."; icon = "🔥"
    
    if uv <= 2:
        if skin_type == "Dry": advice += "\n\n*Hydrating moisturizer SPF 15-30 perfect.*"
        elif skin_type in ["Oily", "Combination"]: advice += "\n\n*Lightweight, oil-free moisturizer SPF 15-30 needed.*"
        elif skin_type == "Sensitive": advice += "\n\n*Gentle, mineral-based moisturizer SPF 15-30 recommended.*"
        else: advice += "\n\n*Light moisturizer SPF 15-30 great.*"
    elif uv <= 5:
        if skin_type == "Dry": advice += "\n\n*Creamy/lotion formula. Reapply frequently!*"
        elif skin_type in ["Oily", "Combination"]: advice += "\n\n*Gel/oil-free formula. Reapply frequently!*"
        elif skin_type == "Sensitive": advice += "\n\n*Mineral SPF 30+ ideal. Reapply frequently!*"
        else: advice += "\n\n*Standard SPF 30+. Reapply frequently!*"
    elif uv <= 7:
        if skin_type == "Dry": advice += "\n\n*Hydrating SPF 50+ & wear a hat.*"
        elif skin_type in ["Oily", "Combination"]: advice += "\n\n*Lightweight/matte SPF 50 & wear a hat.*"
        elif skin_type == "Sensitive": advice += "\n\n*Mineral SPF 50. Shade & hat crucial.*"
        else: advice += "\n\n*SPF 30-50+ & hat recommended.*"
    elif uv <= 10:
        if skin_type == "Sensitive": advice += "\n\n*Mineral SPF 50+, protective clothes, and shade are essential.*"
        else: advice += "\n\n*Hat, sunglasses, reapply SPF 50+ often.*"
    else:
        if skin_type == "Sensitive": advice += "\n\n*Mineral SPF 50+, avoid sun exposure during peak hours.*"
        else: advice += "\n\n*Reapply SPF 50+ every 90 mins outside and seek shelter.*"
    
    return icon, level, advice

def get_environment_advice(humidity, temp, skin_type):
    title_icon = "🌤️"
    advice = ""
    
    # Humidity Advice
    if humidity < 30: 
        advice += "💧 **Dry air concern:** Low humidity pulls moisture from skin, risking dehydration and barrier damage."
        if skin_type == "Dry": advice += "\n\n*Routine focus: Gentle cleanser, Hyaluronic Acid (HA) serum, and a thick moisturizer with ceramides.*"
        elif skin_type in ["Oily", "Combination"]: advice += "\n\n*Routine focus: Use HA serum + a lighter gel-cream/lotion to avoid feeling heavy but maintain hydration.*"
        else: advice += "\n\n*Routine focus: Hydration is key. Look for a non-foaming cleanser, serum, and cream.*"
    elif humidity > 60: 
        advice += "💦 **Humid air concern:** High humidity increases oil production, sweat, and congestion, leading to breakouts."
        if skin_type in ["Oily", "Combination"]: advice += "\n\n*Routine focus: Lightweight, oil-free, non-comedogenic products. A gel moisturizer is ideal.*"
        elif skin_type == "Dry": advice += "\n\n*Routine focus: Use a slightly lighter moisturizer than usual. Cleanse thoroughly at night to remove sweat/oil buildup.*"
        else: advice += "\n\n*Routine focus: Switch to lightweight products (gel-cream or lotion) and ensure good nighttime cleansing.*"
    else: 
        advice += "😌 **Balanced humidity:** Air moisture levels are balanced. Your regular routine should be fine, but still monitor hydration."

    # Temperature Advice
    if temp > 28: 
        advice += "\n\n♨️ **Hot Temperature:** High heat means more sweat. Ensure products are sweat-proof and layered lightly."
    elif temp < 10: 
        advice += "\n\n❄️ **Cold Temperature:** Cold air is often dry and harsh. Protect your skin barrier with occlusion (richer moisturizer) and a scarf."

    return title_icon, advice

def get_wind_advice(wind_speed_ms, skin_type):
    wind_speed_kmh = wind_speed_ms * 3.6
    title_icon = "💨"
    advice = ""
    
    if wind_speed_kmh > 20: 
        advice = f"**Windy! ({wind_speed_kmh:.1f} km/h).** Strong winds cause mechanical irritation and accelerate moisture evaporation (windburn)."
        if skin_type == "Dry": advice += "\n\n*Protection: Apply a thicker, barrier-repair cream (look for ceramides). Don't forget lip balm and hand cream!*"
        elif skin_type == "Sensitive": advice += "\n\n*Protection: Use a soothing, barrier-building moisturizer (like Cica or oat extract) and cover your face with a scarf.*"
        elif skin_type in ["Oily", "Combination"]: advice += "\n\n*Protection: Ensure your moisturizer is effective and consider a protective layer of vaseline or heavier balm on vulnerable areas (cheeks/lips).*"
        else: advice += "\n\n*Protection: Moisturizer and lip balm are key. Consider a protective layer for long exposure.*"
    else: 
        advice = f"**Calm winds ({wind_speed_kmh:.1f} km/h).** No special wind-related precautions needed today."
        title_icon = "🍃"
        
    return title_icon, advice

def get_aqi_advice(aqi, skin_type):
    aqi_levels = {1: "Good (1)", 2: "Fair (2)", 3: "Moderate (3)", 4: "Poor (4)", 5: "Very Poor (5)"}
    level_text = aqi_levels.get(aqi, "Unknown")
    
    title_icon = "🌿"
    if aqi >= 4: title_icon = "🏭"

    advice = f"**Air Quality: {level_text}.** Airborne pollutants generate free radicals that accelerate aging, break down collagen, and cause inflammation."

    # Specific routine tips based on AQI
    if aqi <= 2: 
        advice += "\n\n*Routine: Standard cleansing and SPF routine is fine.*"
    elif aqi == 3: 
        advice += "\n\n*Routine: Be diligent! **AM:** Use an Antioxidant (Vitamin C serum) under your SPF. **PM:** Cleanse thoroughly to remove daily grime.*"
    else: 
        advice += "\n\n*Routine: High pollution risk! **AM:** Antioxidant (Vitamin C) is crucial for defense. **PM:** **Double-cleanse** (oil or micellar water first, then water-based cleanser) to ensure deep removal of pollutants.*"

    # Skin type consideration
    if skin_type == "Sensitive" and aqi > 2: 
        advice += "\n\n*Sensitive Skin Tip: High pollution is irritating. Use gentle Vitamin C derivatives or other mild antioxidants to avoid further redness.*"
        
    return title_icon, level_text, advice

def get_product_recommendations(uv, humidity, skin_type):
    products = {}
    
    # Product 1: SPF/Protection
    if uv <= 2: products['product1_name'] = "Moisturizer w/ SPF"; products['product1_desc'] = "A lightweight SPF 15-30."
    elif uv <= 7: products['product1_name'] = "SPF 30-50"; products['product1_desc'] = "A dedicated daily broad-spectrum protector."
    else: products['product1_name'] = "SPF 50+"; products['product1_desc'] = "Heavy-duty, water-resistant formula. Reapply every 2 hours!"
    
    if uv <= 2 and skin_type == "Sensitive": products['product1_desc'] += " *Mineral-based preferred.*"
    elif uv <= 7 and skin_type in ["Oily", "Combination"]: products['product1_desc'] += " *Oil-free/gel preferred.*"
    elif uv > 7 and skin_type == "Sensitive": products['product1_desc'] += " *Mineral, water-resistant preferred.*"

    # Product 2: Hydration/Cleansing adjustment
    if humidity < 30: # Dry air
        if skin_type in ["Dry", "Sensitive"]: products['product2_name'] = "Hydrating Cleanser & Rich Cream"; products['product2_desc'] = "Non-foaming cleanser + a thick, barrier-focused ceramide cream."
        else: products['product2_name'] = "Gentle Cleanser & HA Serum"; products['product2_desc'] = "Gentle cleanser + a hydrating serum (HA/Glycerin) topped with a light cream/lotion."
    elif humidity > 60: # Humid air
        if skin_type in ["Oily", "Combination"]: products['product2_name'] = "Gel/Foam Cleanser & Oil-Free Gel"; products['product2_desc'] = "Foaming/gel cleanser + a featherlight, oil-free gel moisturizer."
        else: products['product2_name'] = "Gentle Cleanser & Lightweight Lotion"; products['product2_desc'] = "Gentle cleanser + a light lotion/gel-cream to prevent heaviness."
    else: # Balanced
        if skin_type == "Dry": products['product2_name'] = "Hydrating Cleanser & Standard Moisturizer"; products['product2_desc'] = "Your usual hydrating cleanser and daily cream are perfect."
        elif skin_type == "Oily": products['product2_name'] = "Gentle Foaming Cleanser & Light Moisturizer"; products['product2_desc'] = "Your preferred foaming cleanser + a lightweight lotion/gel."
        else: products['product2_name'] = "Go-To Cleanser & Moisturizer"; products['product2_desc'] = "Your standard, tried-and-true products are ideal."
        
    return products

# --- Main Streamlit App ---
def main():
    load_css() # Load the enhanced theme

    # Header with Custom Font & Color
    st.markdown("""
    <div style="text-align:center; margin-top:0.5rem; margin-bottom:1.25rem;">
        <div style="font-family: var(--font-heading); color:#957DAD; font-weight:650; letter-spacing:4px; text-transform:uppercase; font-size:clamp(1.0rem, 3.5vw, 2.0rem); text-shadow: 0 6px 20px rgba(149,125,173,0.25);">DermacScribe</div>
        <div style="font-family: var(--font-heading); color:#4A3F5E; font-weight:700; letter-spacing:1px; font-size:clamp(2.0rem, 6.1vw, 3.2rem); margin-top:0.3rem; text-shadow: 0 8px 30px rgba(74,63,94,0.08);">Skin Health Advisor</div>
    </div>""", unsafe_allow_html=True)

    if hero_image:
        st.image(hero_image, use_container_width=True, caption="Your Personal Skincare Forecast") # Updated caption
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.1rem; max-width: 700px; margin: -1rem auto 2rem auto;'>Get personalized skincare advice based on your local weather and environmental risks.</p>", unsafe_allow_html=True)

    api_key = st.secrets.get("OPENWEATHER_API_KEY")
    if not api_key:
        st.markdown('<div class="custom-alert custom-error">API key missing. Check secrets.toml.</div>', unsafe_allow_html=True)
        st.stop()

    # User Input Card
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top: 0; text-align: center;'>Your Details</h3>", unsafe_allow_html=True)
        col_input1, col_input2 = st.columns(2)
        with col_input1: skin_type = st.selectbox("Skin Type:", ("Normal", "Oily", "Dry", "Combination", "Sensitive"))
        with col_input2: location_option = st.radio("Location Method:", ("Automatically find me", "Enter city manually"), horizontal=True)
        lat, lon, error, location_name = None, None, None, None
        city_input_placeholder = st.empty()
        
        # Location Logic (Unchanged)
        if location_option == "Automatically find me":
            city_input_placeholder.markdown('<div class="custom-alert custom-info" style="text-align: center;">Allow browser location access.</div>', unsafe_allow_html=True)
            with st.spinner("Waiting for location..."): loc = get_geolocation()
            if loc:
                lat, lon = loc['coords']['latitude'], loc['coords']['longitude']; location_name = "your current location"
                city_input_placeholder.markdown(f'<div class="custom-alert custom-success">Location found!</div>', unsafe_allow_html=True)
            else:
                city_input_placeholder.markdown('<div class="custom-alert custom-warning">Could not get location. Enter city manually.</div>', unsafe_allow_html=True); error = True
        else:
            city = city_input_placeholder.text_input("Enter City:", key="city_manual")
            if city:
                lat, lon, error_msg = get_coordinates(city, api_key)
                if not error_msg: location_name = city.title()
                else: st.markdown(f'<div class="custom-alert custom-error">{error_msg}</div>', unsafe_allow_html=True); error = True
            else: error = True
        st.markdown('</div>', unsafe_allow_html=True)

    # Submit Button
    _, center_col, _ = st.columns([1, 11, 1])
    with center_col:
        button_disabled = bool(error) or (lat is None or lon is None)
        if st.button(f"Get My {skin_type} Skin Forecast 🔮", type="primary", use_container_width=True, disabled=button_disabled): # Added icon to button
            with st.spinner(f"Analyzing weather for {skin_type.lower()} skin..."): data = get_weather_data(lat, lon, api_key)
            if data["error"]: st.markdown(f'<div class="custom-alert custom-error">{data["error"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="custom-alert custom-success" style="text-align:center;">**Report Generated for {location_name}!** Scroll down for your personalized routine.</div>', unsafe_allow_html=True); st.divider()
                
                # Generate advice with new visual cues
                uv_icon, uv_level, uv_advice = get_uv_advice(data['uv'], skin_type)
                env_icon, env_advice = get_environment_advice(data['humidity'], data['temp'], skin_type)
                wind_icon, wind_advice = get_wind_advice(data['wind_speed'], skin_type)
                aqi_icon, aqi_level, aqi_advice = get_aqi_advice(data['aqi'], skin_type)
                products = get_product_recommendations(data['uv'], data['humidity'], skin_type)

                st.subheader("Current Environmental Report")
                
                # --- ENHANCED METRIC LAYOUT (5 uniform columns, now wider due to CSS change) ---
                col_met1, col_met2, col_met3, col_met4, col_met5 = st.columns(5)

                col_met1.metric(label="UV Index", value=f"{data['uv']:.1f}", delta=uv_level.split(" ")[0], delta_color="inverse")
                col_met2.metric(label="Temperature", value=f"{data['temp']:.1f} °C")
                col_met3.metric(label="Humidity", value=f"{data['humidity']} %")
                col_met4.metric(label="Wind Speed", value=f"{data['wind_speed']*3.6:.1f} km/h")
                col_met5.metric(label="Air Quality (AQI)", value=f"{data['aqi']}", delta=aqi_level.split(" ")[0], delta_color="inverse")

                st.caption(f"**Current Weather:** {data['description'].title()}")
                st.divider()

                # --- VISUALLY APPEALING ADVICE CARDS ---
                st.subheader(f"Daily Skincare Plan for {skin_type} Skin")
                
                # Use updated markdown for visual cards with icons
                advice_html_template = '<div class="advice-card"><h3><span class="icon">{icon}</span> {title}</h3><p>{advice}</p></div>'

                # UV Advice Card
                st.markdown(advice_html_template.format(
                    icon=uv_icon, 
                    title="UV Protection Strategy", 
                    advice=uv_advice.replace('\n\n', '<br>')
                ), unsafe_allow_html=True)
                
                # Environment (Temp & Humidity) Card
                st.markdown(advice_html_template.format(
                    icon=env_icon, 
                    title="Hydration & Barrier Advisory", 
                    advice=env_advice.replace('\n\n', '<br>')
                ), unsafe_allow_html=True)
                
                # Wind Advisory Card
                st.markdown(advice_html_template.format(
                    icon=wind_icon, 
                    title="Wind & Irritation Guard", 
                    advice=wind_advice.replace('\n\n', '<br>')
                ), unsafe_allow_html=True)
                
                # Air Pollution Card
                st.markdown(advice_html_template.format(
                    icon=aqi_icon, 
                    title="Pollution Defense & Cleansing", 
                    advice=aqi_advice.replace('\n\n', '<br>')
                ), unsafe_allow_html=True)


                st.subheader("💡 Suggested Product Types")
                with st.expander(f"**Click to View Key Product Recommendations for {skin_type} Skin**"):
                    st.markdown(f"**1. Essential Protector ({products['product1_name']})**: {products['product1_desc']}")
                    st.markdown(f"**2. Cleanser/Moisturizer Adjustment ({products['product2_name']})**: {products['product2_desc']}")
                    st.markdown('<div class="custom-alert custom-warning">Note: These are product *types*. Choose specific products you know work well with your skin\'s known sensitivities.</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()