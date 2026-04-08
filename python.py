import streamlit as st
import requests
import json
import urllib.parse
from typing import Dict, List, Optional

st.set_page_config(
    page_title="TrendWeave AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

FEATURE_SUGGESTIONS = {
    "Summer": ["Moisture-friendly fabric finish", "Breathable inner construction", "Easy day-to-night styling"],
    "Winter": ["Thermal comfort layering", "Structured silhouette retention", "Functional outerwear detailing"],
    "Spring": ["Transitional layering flexibility", "Soft movement in fabric", "Fresh color contrast styling"],
    "Autumn": ["Texture-led styling", "Mid-weather adaptability", "Utility-inspired pocket details"]
}

if "generated" not in st.session_state:
    st.session_state.generated = False
if "result" not in st.session_state:
    st.session_state.result = None
if "refs" not in st.session_state:
    st.session_state.refs = []
if "submitted_inputs" not in st.session_state:
    st.session_state.submitted_inputs = {}


def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at top center, rgba(99, 102, 241, 0.14), transparent 24%),
            radial-gradient(circle at left top, rgba(56, 189, 248, 0.08), transparent 18%),
            linear-gradient(135deg, #0b1120 0%, #111827 45%, #0f172a 100%);
        color: #f8fafc;
    }

    .block-container {
        max-width: 1240px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    section[data-testid="stSidebar"] { display: none; }

    .hero-card, .clean-card, .feature-card, .image-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        box-shadow: 0 12px 32px rgba(2, 6, 23, 0.24);
    }

    .hero-card {
        border-radius: 28px;
        padding: 2rem;
        text-align: center;
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

    .pill, .badge {
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

    .clean-card, .feature-card, .image-card {
        border-radius: 22px;
        padding: 1.15rem;
        margin-bottom: 1rem;
    }

    .feature-card { min-height: 130px; text-align: center; }
    .feature-title, .section-title, .sub-title, .result-title { color: #fff; }
    .feature-title, .section-title, .sub-title { font-weight: 700; }
    .feature-desc, .result-text, .info-line, .image-caption { color: rgba(226,232,240,0.84); }
    .result-title { font-size: 1.28rem; font-weight: 800; margin-bottom: 0.65rem; }
    .result-text, .info-line { line-height: 1.72; }
    .section-title { text-align: center; font-size: 1.08rem; margin-bottom: 0.9rem; }
    .sub-title { font-size: 1rem; margin-bottom: 0.65rem; }

    .metric-box {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 1rem;
        text-align: center;
    }

    .metric-label { color: rgba(226,232,240,0.68); font-size: 0.8rem; margin-bottom: 0.32rem; }
    .metric-value { color: #ffffff; font-size: 1rem; font-weight: 700; }

    .image-card { overflow: hidden; padding: 0; }
    .image-caption { padding: 0.85rem 1rem 1rem 1rem; font-size: 0.9rem; text-align: center; }

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
    </style>
    """, unsafe_allow_html=True)


def get_weather(city: str) -> Optional[Dict[str, str]]:
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
        current = weather_res.json().get("current", {})
        return {
            "temperature": current.get("temperature_2m", "N/A"),
            "wind_speed": current.get("wind_speed_10m", "N/A")
        }
    except Exception:
        return None


def demo_result(prompt_inputs: Dict[str, str]) -> Dict:
    season = prompt_inputs.get("season", "Summer")
    style = prompt_inputs.get("style", "Streetwear")
    demographic = prompt_inputs.get("demographic", "Gen Z")
    return {
        "design_name": f"{season} {style} Edit",
        "concept": f"A {season.lower()}-ready {style.lower()} outfit concept tailored for {demographic.lower()} shoppers, balancing trend-forward styling, practical comfort, and easy commercial production.",
        "colors": ["Powder Blue", "Soft White", "Stone Beige"],
        "fabrics": FABRIC_GUIDE[season][:2],
        "size_recommendation": SIZE_GUIDE[demographic],
        "production_feasibility": "High feasibility with low-to-medium construction complexity and locally sourceable materials.",
        "target_demographic": f"{demographic} fashion shoppers",
        "suggested_features": FEATURE_SUGGESTIONS[season],
        "style_notes": [
            "Keep the silhouette clean and camera-friendly for social media appeal.",
            "Use contrast between base neutral tones and one soft statement shade.",
            "Balance comfort, repeat wearability, and trend relevance."
        ],
        "debug_error": "Demo mode active - add GROQ_API_KEY in Streamlit secrets to enable live AI generation."
    }


def generate_outfit_reference_images(season: str, style: str, demographic: str, gender: str) -> List[Dict[str, str]]:
    queries = [
        f"{season.lower()} {style.lower()} outfit {gender.lower()} fashion",
        f"{demographic.lower()} street style outfit photography",
        f"editorial fashion outfit full body {style.lower()} look"
    ]
    refs = []
    for q in queries:
        encoded = urllib.parse.quote(q)
        refs.append({
            "url": f"https://source.unsplash.com/featured/1200x900/?{encoded}",
            "caption": q.title()
        })
    return refs


def generate_design(prompt: str, prompt_inputs: Dict[str, str]) -> Dict:
    if not GROQ_API_KEY:
        return demo_result(prompt_inputs)

    api_url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    system_message = """
You are a professional fashion intelligence assistant for a hackathon demo app.
Return only valid JSON with this exact schema:
{
  "design_name": "string",
  "concept": "string",
  "colors": ["string", "string", "string"],
  "fabrics": ["string", "string"],
  "size_recommendation": "string",
  "production_feasibility": "string",
  "target_demographic": "string",
  "suggested_features": ["string", "string", "string"],
  "style_notes": ["string", "string", "string"]
}
Rules:
- Keep concept under 90 words.
- Suggested features must be realistic fashion product features, not software features.
- Colors and fabrics must be production-friendly.
- Output JSON only.
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
            data = demo_result(prompt_inputs)
            data["debug_error"] = f"HTTP {response.status_code}: {result}"
            return data

        content = result["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        parsed["debug_error"] = "Success - Groq JSON mode"
        return parsed
    except Exception as e:
        data = demo_result(prompt_inputs)
        data["debug_error"] = f"Groq fallback triggered: {str(e)}"
        return data


load_css()

st.markdown("""
<div class="hero-card">
    <div>
        <span class="pill">AI Fashion Intelligence</span>
        <span class="pill">Groq JSON Mode</span>
        <span class="pill">Outfit Moodboard</span>
        <span class="pill">Hackathon Ready</span>
    </div>
    <div class="hero-title">TrendWeave AI</div>
    <div class="hero-sub">
        A fashion design intelligence platform that transforms trend, demographic, weather, and regional inputs
        into outfit concepts with materials, color palette, sizing guidance, production feasibility, and visual references.
    </div>
</div>
""", unsafe_allow_html=True)

fc1, fc2, fc3 = st.columns(3, gap="large")
with fc1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">Trend Analysis</div>
        <div class="feature-desc">Uses seasonal and audience signals to shape commercial fashion direction.</div>
    </div>
    """, unsafe_allow_html=True)
with fc2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">AI Design Output</div>
        <div class="feature-desc">Generates concept, color palette, fabrics, styling notes, and outfit features.</div>
    </div>
    """, unsafe_allow_html=True)
with fc3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">Outfit Moodboard</div>
        <div class="feature-desc">Shows reference imagery focused on real outfit photography rather than random placeholders.</div>
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

st.markdown('</div>', unsafe_allow_html=True)

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
        <div class="metric-value">{'Groq Live' if GROQ_API_KEY else 'Demo'}</div>
    </div>
    """, unsafe_allow_html=True)

if generate:
    prompt_inputs = {
        "demographic": demographic,
        "gender": gender,
        "season": season,
        "region": region,
        "style": style,
        "price_range": price_range,
        "temp_text": temp_text,
        "wind_text": wind_text
    }
    prompt = f"""
Create an original fashion outfit design for the following input.
Season: {season}
Style: {style}
Gender segment: {gender}
Target demographic: {demographic}
Region: {region}
Trend keywords: {', '.join(TREND_DATA[season])}
Suggested fabrics: {', '.join(FABRIC_GUIDE[season])}
Suggested sizes: {SIZE_GUIDE[demographic]}
Price range: {price_range}
Current weather: {temp_text}
Wind speed: {wind_text}
Need: one commercially realistic outfit concept suitable for a fashion design ideation tool.
"""
    result = generate_design(prompt, prompt_inputs)
    refs = generate_outfit_reference_images(season, style, demographic, gender)
    st.session_state.generated = True
    st.session_state.result = result
    st.session_state.refs = refs
    st.session_state.submitted_inputs = prompt_inputs

if st.session_state.generated and st.session_state.result:
    result = st.session_state.result
    refs = st.session_state.refs
    submitted = st.session_state.submitted_inputs

    st.markdown("## Generated Output")

    o1, o2 = st.columns(2, gap="large")
    with o1:
        st.markdown('<div class="clean-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="result-title">{result.get("design_name", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-text">{result.get("concept", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="info-line"><b>Target Demographic:</b> {result.get("target_demographic", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-line"><b>Size Recommendation:</b> {result.get("size_recommendation", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-line"><b>Region:</b> {submitted.get("region", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with o2:
        st.markdown('<div class="clean-card">', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Materials & Production</div>', unsafe_allow_html=True)
        colors = result.get("colors", [])
        fabrics = result.get("fabrics", [])
        colors = colors if isinstance(colors, list) else [str(colors)]
        fabrics = fabrics if isinstance(fabrics, list) else [str(fabrics)]
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
        st.markdown('<div class="sub-title">Suggested Outfit Features</div>', unsafe_allow_html=True)
        st.markdown("".join([f'<span class="badge">{item}</span>' for item in result.get("suggested_features", [])]), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with ti2:
        st.markdown('<div class="clean-card">', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Styling Notes</div>', unsafe_allow_html=True)
        for note in result.get("style_notes", []):
            st.markdown(f'- {note}')
        st.markdown('</div>', unsafe_allow_html=True)
    with ti3:
        st.markdown('<div class="clean-card">', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Weather Context</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-line"><b>Season:</b> {submitted.get("season", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-line"><b>Temperature:</b> {submitted.get("temp_text", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-line"><b>Wind Speed:</b> {submitted.get("wind_text", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("## Reference Moodboard")
    im1, im2, im3 = st.columns(3, gap="large")
    for col, item in zip([im1, im2, im3], refs):
        with col:
            st.markdown('<div class="image-card">', unsafe_allow_html=True)
            st.image(item["url"], width="stretch")
            st.markdown(f'<div class="image-caption">{item["caption"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("## System Status")
    st.markdown('<div class="clean-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="debug-box">{result.get("debug_error", "No debug message")}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    pv1, pv2, pv3 = st.columns(3, gap="large")
    with pv1:
        st.markdo
