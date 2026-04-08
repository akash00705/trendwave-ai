import streamlit as st
import requests
import json
import urllib.parse

st.set_page_config(
    page_title="TrendWeave AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "generated_result" not in st.session_state:
    st.session_state.generated_result = None

if "generated_refs" not in st.session_state:
    st.session_state.generated_refs = None

if "last_generated" not in st.session_state:
    st.session_state.last_generated = False

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = ""

GROQ_MODEL = "llama-3.1-8b-instant"

TREND_DATA = {
    "Summer": ["Pastel tones", "Oversized silhouettes", "Breathable fabrics", "Minimal streetwear"],
    "Winter": ["Layered fits", "Earth tones", "Wool blends", "Structured outerwear"],
    "Spring": ["Floral accents", "Light denim", "Soft colors", "Relaxed tailoring"],
    "Autumn": ["Muted palettes", "Knit textures", "Cargo details", "Transitional layering"]
}

SIZE_GUIDE = {
    "Gen Z": "XS to L with relaxed and oversized fits",
    "Working Professionals": "S to XL with structured regular fits",
    "Teens": "XS to M with comfort-focused fits",
    "Adults": "S to XXL with inclusive size balance"
}

FABRIC_GUIDE = {
    "Summer": ["Cotton", "Linen", "Rayon"],
    "Winter": ["Wool Blend", "Fleece", "Corduroy"],
    "Spring": ["Cotton Blend", "Light Denim", "Viscose"],
    "Autumn": ["Knit Fabric", "Twill", "Poly-Cotton Blend"]
}

def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at top center, rgba(99, 102, 241, 0.16), transparent 26%),
            radial-gradient(circle at left top, rgba(56, 189, 248, 0.10), transparent 20%),
            linear-gradient(135deg, #0b1120 0%, #111827 45%, #0f172a 100%);
        color: #f8fafc;
    }

    .block-container {
        max-width: 1240px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    section[data-testid="stSidebar"] {
        display: none;
    }

    .hero-card {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 28px;
        padding: 2rem;
        text-align: center;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        box-shadow: 0 12px 32px rgba(2, 6, 23, 0.30);
        margin-bottom: 1.25rem;
    }

    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #ffffff;
        margin-bottom: 0.55rem;
    }

    .hero-sub {
        max-width: 820px;
        margin: 0 auto;
        color: rgba(226,232,240,0.82);
        font-size: 1rem;
        line-height: 1.75;
    }

    .pill-wrap {
        margin-bottom: 1rem;
    }

    .pill {
        display: inline-block;
        padding: 0.42rem 0.88rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.10);
        color: #dbeafe;
        font-size: 0.82rem;
        font-weight: 600;
        margin: 0.22rem;
    }

    .clean-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 22px;
        padding: 1.2rem;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        box-shadow: 0 8px 24px rgba(2, 6, 23, 0.24);
        margin-bottom: 1rem;
    }

    .feature-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 22px;
        padding: 1.1rem;
        min-height: 130px;
        text-align: center;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
    }

    .feature-title {
        color: #ffffff;
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }

    .feature-desc {
        color: rgba(226,232,240,0.76);
        font-size: 0.92rem;
        line-height: 1.55;
    }

    .section-title {
        text-align: center;
        color: #ffffff;
        font-size: 1.08rem;
        font-weight: 700;
        margin-bottom: 0.9rem;
    }

    .sub-title {
        color: #ffffff;
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 0.65rem;
    }

    .metric-box {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 1rem;
        text-align: center;
    }

    .metric-label {
        color: rgba(226,232,240,0.68);
        font-size: 0.8rem;
        margin-bottom: 0.32rem;
    }

    .metric-value {
        color: #ffffff;
        font-size: 1rem;
        font-weight: 700;
    }

    .badge {
        display: inline-block;
        padding: 0.42rem 0.78rem;
        margin: 0.2rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.10);
        color: #f8fafc;
        font-size: 0.82rem;
    }

    .result-title {
        color: #ffffff;
        font-size: 1.28rem;
        font-weight: 800;
        margin-bottom: 0.65rem;
    }

    .result-text {
        color: rgba(226,232,240,0.86);
        font-size: 0.96rem;
        line-height: 1.72;
    }

    .info-line {
        color: #e2e8f0;
        font-size: 0.95rem;
        line-height: 1.75;
    }

    .image-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 22px;
        overflow: hidden;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
    }

    .image-caption {
        padding: 0.85rem 1rem 1rem 1rem;
        color: #e2e8f0;
        font-size: 0.9rem;
        text-align: center;
    }

    .debug-box {
        background: rgba(15, 23, 42, 0.72);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1rem;
        color: #cbd5e1;
        font-family: monospace;
        font-size: 0.86rem;
        white-space: pre-wrap;
        word-break: break-word;
    }

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    .stTextInput > div > div,
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 16px !important;
        min-height: 48px;
    }

    input, textarea, [data-baseweb="input"] input {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #ffffff !important;
        font-size: 15px !important;
    }

    input::placeholder, textarea::placeholder {
        color: rgba(226,232,240,0.45) !important;
        -webkit-text-fill-color: rgba(226,232,240,0.45) !important;
    }

    .stTextInput label, .stSelectbox label {
        color: #dbe4f0 !important;
        font-weight: 600 !important;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        width: 100%;
        border-radius: 16px;
        padding: 0.8rem 1rem;
        font-size: 1rem;
        font-weight: 700;
        border: 1px solid rgba(255,255,255,0.12);
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        color: #ffffff;
        box-shadow: 0 12px 30px rgba(37, 99, 235, 0.28);
    }

    label, p, span, div {
        color: #e2e8f0;
    }

    @media (max-width: 900px) {
        .hero-title {
            font-size: 2.15rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def get_weather(city):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(city)}&count=1"
        geo_res = requests.get(geo_url, timeout=20)
        geo_data = geo_res.json()

        if "results" not in geo_data:
            return None

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m"
        )
        weather_res = requests.get(weather_url, timeout=20)
        weather_data = weather_res.json()
        current = weather_data.get("current", {})

        return {
            "temperature": current.get("temperature_2m", "N/A"),
            "wind_speed": current.get("wind_speed_10m", "N/A")
        }
    except Exception:
        return None

def demo_result():
    return {
        "design_name": "Urban Breeze Co-ord Set",
        "concept": "A premium summer streetwear co-ord set for Gen Z with oversized comfort, breathable tailoring, pastel layering, and social-ready styling.",
        "colors": ["Powder Blue", "Soft White", "Sand Beige"],
        "fabrics": ["Cotton Poplin", "Linen Blend"],
        "size_recommendation": "XS to L with relaxed oversized fit",
        "production_feasibility": "High feasibility with low-to-medium stitching complexity and easy local sourcing",
        "target_demographic": "Gen Z urban fashion shoppers",
        "feature_suggestions": [
            "Oversized cropped shirt",
            "Wide-leg coordinated shorts",
            "Utility pocket detailing",
            "Lightweight layered styling"
        ],
        "debug_error": "Demo mode active"
    }

def generate_reference_images(season, style, demographic, gender):
    queries = [
        f"{season} {style} {gender} outfit",
        f"{demographic} {style} fashion outfit",
        f"{season} street style outfit photo"
    ]

    refs = []
    for q in queries:
        encoded = urllib.parse.quote(q)
        refs.append({
            "url": f"https://source.unsplash.com/900x700/?{encoded}",
            "caption": q.title()
        })
    return refs

def generate_design(prompt):
    if not GROQ_API_KEY:
        return demo_result()

    api_url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    system_message = """
You are a professional fashion intelligence assistant.
Return only valid JSON.
Use this exact schema:
{
  "design_name": "string",
  "concept": "string",
  "colors": ["string", "string", "string"],
  "fabrics": ["string", "string"],
  "size_recommendation": "string",
  "production_feasibility": "string",
  "target_demographic": "string",
  "feature_suggestions": ["string", "string", "string", "string"]
}
"""

    payload = {
        "model": GROQ_MODEL,
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        result = response.json()

        if response.status_code != 200:
            data = demo_result()
            data["debug_error"] = f"HTTP {response.status_code}: {result}"
            return data

        content = result["choices"][0]["message"]["content"]
        parsed = json.loads(content)

        parsed["debug_error"] = "Success"
        return parsed

    except Exception as e:
        data = demo_result()
        data["debug_error"] = str(e)
        return data

load_css()

st.markdown("""
<div class="hero-card">
    <div class="pill-wrap">
        <span class="pill">AI Fashion Intelligence</span>
        <span class="pill">Clean Main Layout</span>
        <span class="pill">Outfit Moodboard</span>
        <span class="pill">Groq Powered</span>
    </div>
    <div class="hero-title">TrendWeave AI</div>
    <div class="hero-sub">
        A clean fashion design intelligence platform that transforms trends, demographics, regional context,
        and seasonal inputs into original fashion concepts with fabrics, sizing guidance, production feasibility,
        features, and outfit-photo references.
    </div>
</div>
""", unsafe_allow_html=True)

fc1, fc2, fc3 = st.columns(3, gap="large")
with fc1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">Trend Analysis</div>
        <div class="feature-desc">Uses seasonal and audience signals to shape modern design direction.</div>
    </div>
    """, unsafe_allow_html=True)
with fc2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">AI Feature Suggestions</div>
        <div class="feature-desc">Generates concept, colors, fabrics, outfit features, and feasibility insights.</div>
    </div>
    """, unsafe_allow_html=True)
with fc3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">Outfit Moodboard</div>
        <div class="feature-desc">Shows outfit-style reference photos instead of generic random placeholders.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="clean-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Design Configuration</div>', unsafe_allow_html=True)

with st.form("fashion_form"):
    row1_col1, row1_col2, row1_col3 = st.columns(3, gap="large")
    with row1_col1:
        demographic = st.selectbox("Target Demographic", ["Gen Z", "Working Professionals", "Teens", "Adults"])
    with row1_col2:
        gender = st.selectbox("Gender Segment", ["Women", "Men", "Unisex"])
    with row1_col3:
        season = st.selectbox("Season", ["Summer", "Winter", "Spring", "Autumn"])

    row2_col1, row2_col2, row2_col3 = st.columns(3, gap="large")
    with row2_col1:
        region = st.text_input("Region / City", "Coimbatore")
    with row2_col2:
        style = st.selectbox("Style Preference", ["Streetwear", "Minimal", "Casual", "Ethnic Fusion", "Formal"])
    with row2_col3:
        price_range = st.selectbox("Price Range", ["Budget", "Mid-range", "Premium"])

    generate = st.form_submit_button("Generate Fashion Design")

weather = get_weather(region)
temp_text = f"{weather['temperature']}°C" if weather else "Unavailable"
wind_text = f"{weather['wind_speed']} km/h" if weather else "Unavailable"

mc1, mc2, mc3 = st.columns(3, gap="large")
with mc1:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Selected Season</div>
        <div class="metric-value">{season}</div>
    </div>
    """, unsafe_allow_html=True)
with mc2:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Temperature Context</div>
        <div class="metric-value">{temp_text}</div>
    </div>
    """, unsafe_allow_html=True)
with mc3:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">AI Mode</div>
        <div class="metric-value">{'Groq' if GROQ_API_KEY else 'Demo'}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

if generate:
    prompt = f"""
Create an original {season} {style} fashion design for {gender} targeting {demographic} in {region}.
Trend keywords: {', '.join(TREND_DATA[season])}
Suggested fabrics: {', '.join(FABRIC_GUIDE[season])}
Suggested sizes: {SIZE_GUIDE[demographic]}
Price range: {price_range}
Current weather: {temp_text}
Wind speed: {wind_text}

Also suggest 4 practical outfit features or garment details suitable for this fashion concept.
"""

    result = generate_design(prompt)
    refs = generate_reference_images(season, style, demographic, gender)

    st.session_state.generated_result = result
    st.session_state.generated_refs = refs
    st.session_state.last_generated = True

if st.session_state.last_generated and st.session_state.generated_result:
    result = st.session_state.generated_result
    refs = st.session_state.generated_refs

    st.markdown("## Generated Output")

    o1, o2 = st.columns(2, gap="large")
    with o1:
        st.markdown('<div class="clean-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="result-title">{result.get("design_name", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-text">{result.get("concept", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="info-line"><b>Target Demographic:</b> {result.get("target_demographic", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-line"><b>Size Recommendation:</b> {result.get("size_recommendation", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with o2:
        st.markdown('<div class="clean-card">', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Materials & Production</div>', unsafe_allow_html=True)

        colors = result.get("colors", [])
        fabrics = result.get("fabrics", [])
        features = result.get("feature_suggestions", [])

        if not isinstance(colors, list):
            colors = [str(colors)]
        if not isinstance(fabrics, list):
            fabrics = [str(fabrics)]
        if not isinstance(features, list):
            features = [str(features)]

        st.markdown("**Color Palette**")
        st.markdown("".join([f'<span class="badge">{c}</span>' for c in colors]), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Fabric Suggestions**")
        st.markdown("".join([f'<span class="badge">{f}</span>' for f in fabrics]), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="info-line"><b>Production Feasibility:</b> {result.get("production_feasibility", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    ti1, ti2, ti3 = st.columns(3, gap="large")
    with ti1:
        st.markdown('<div class="clean-card">', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Trend Keywords</div>', unsafe_allow_html=True)
        st.markdown("".join([f'<span class="badge">{item}</span>' for item in TREND_DATA[season]]), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with ti2:
        st.markdown('<div class="clean-card">', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">AI Feature Suggestions</div>', unsafe_allow_html=True)
        st.markdown("".join([f'<span class="badge">{item}</span>' for item in features]), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with ti3:
        st.markdown('<div class="clean-card">', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Weather Context</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-line"><b>Region:</b> {region}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-line"><b>Temperature:</b> {temp_text}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-line"><b>Wind Speed:</b> {wind_text}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("## Reference Moodboard")
    im1, im2, im3 = st.columns(3, gap="large")
    for col, item in zip([im1, im2, im3], refs):
        with col:
            st.markdown('<div class="image-card">', unsafe_allow_html=True)
            st.image(item["url"], use_container_width=True)
            st.markdown(f'<div class="image-caption">{item["caption"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("## System Status")
    st.markdown('<div class="clean-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="debug-box">{result.get("debug_error", "No debug message")}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    pv1, pv2, pv3 = st.columns(3, gap="large")
    with pv1:
        st.markdown('<div cla
