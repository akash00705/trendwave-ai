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

STYLE_GUIDE = {
    "Streetwear": [
        "Relaxed silhouette with trend-led layering",
        "Strong visual appeal for social-first styling",
        "Commercially versatile everyday statement look"
    ],
    "Minimal": [
        "Clean lines and controlled palette",
        "Refined silhouettes with subtle detailing",
        "Quiet luxury feel at accessible production level"
    ],
    "Casual": [
        "Comfort-driven wardrobe essential",
        "Easy repeat wear and broad commercial appeal",
        "Low-risk, mass-friendly styling direction"
    ],
    "Ethnic Fusion": [
        "Modern silhouette with cultural styling cues",
        "Contemporary fabric pairing with traditional influence",
        "Festive-ready while still wearable for everyday occasions"
    ],
    "Formal": [
        "Sharp structure with polished detailing",
        "Professional and occasion-ready fit direction",
        "Elevated styling with durable material choices"
    ]
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
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(180deg, #0b1120 0%, #111827 100%);
        color: #f8fafc;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    section[data-testid="stSidebar"] {
        display: none;
    }

    .main-shell {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
    }

    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.35rem;
        text-align: center;
        letter-spacing: -0.02em;
    }

    .hero-subtitle {
        text-align: center;
        font-size: 1rem;
        color: rgba(226,232,240,0.78);
        max-width: 760px;
        margin: 0 auto 1.75rem auto;
        line-height: 1.7;
    }

    .section-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }

    .result-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 1.35rem;
        height: 100%;
        backdrop-filter: blur(8px);
    }

    .section-title {
        font-size: 1rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 1rem;
    }

    .design-title {
        font-size: 1.4rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.75rem;
    }

    .muted-text {
        color: rgba(226,232,240,0.80);
        line-height: 1.75;
        font-size: 0.97rem;
    }

    .info-item {
        color: rgba(226,232,240,0.84);
        line-height: 1.8;
        font-size: 0.95rem;
        margin-bottom: 0.35rem;
    }

    .badge-wrap {
        margin-top: 0.35rem;
    }

    .badge {
        display: inline-block;
        padding: 0.42rem 0.8rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.10);
        color: #e2e8f0;
        font-size: 0.82rem;
        font-weight: 600;
        margin: 0.2rem 0.28rem 0.2rem 0;
    }

    .metric-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 18px;
        padding: 1rem;
        text-align: center;
        height: 100%;
    }

    .metric-label {
        color: rgba(226,232,240,0.66);
        font-size: 0.8rem;
        margin-bottom: 0.3rem;
    }

    .metric-value {
        color: #ffffff;
        font-size: 1rem;
        font-weight: 700;
    }

    .preview-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 1.2rem;
        min-height: 180px;
        height: 100%;
    }

    .preview-title {
        color: #ffffff;
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 0.65rem;
    }

    .preview-text {
        color: rgba(226,232,240,0.80);
        line-height: 1.7;
        font-size: 0.94rem;
    }

    .image-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 0.8rem;
        height: 100%;
    }

    .image-caption {
        color: rgba(226,232,240,0.78);
        text-align: center;
        font-size: 0.88rem;
        margin-top: 0.75rem;
    }

    .status-box {
        background: rgba(15, 23, 42, 0.78);
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
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 14px !important;
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
        border-radius: 14px;
        padding: 0.8rem 1rem;
        font-size: 1rem;
        font-weight: 700;
        border: none;
        background: #2563eb;
        color: #ffffff;
        box-shadow: none;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background: #1d4ed8;
    }

    h2, h3 {
        color: #ffffff;
        margin-top: 0.6rem;
        margin-bottom: 0.85rem;
    }

    .small-note {
        color: rgba(226,232,240,0.70);
        font-size: 0.88rem;
        margin-top: 0.35rem;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def safe_str(value) -> str:
    if value is None:
        return "N/A"
    return str(value)


def get_weather(city: str) -> Optional[Dict[str, str]]:
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(city)}&count=1"
        geo_res = requests.get(geo_url, timeout=20)
        geo_res.raise_for_status()
        geo_data = geo_res.json()

        if "results" not in geo_data or not geo_data["results"]:
            return None

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m"
        )
        weather_res = requests.get(weather_url, timeout=20)
        weather_res.raise_for_status()
        current = weather_res.json().get("current", {})

        temperature = current.get("temperature_2m")
        wind_speed = current.get("wind_speed_10m")

        return {
            "temperature": safe_str(temperature) if temperature is not None else "N/A",
            "wind_speed": safe_str(wind_speed) if wind_speed is not None else "N/A"
        }
    except Exception:
        return None


def demo_result(prompt_inputs: Dict[str, str]) -> Dict:
    season = prompt_inputs.get("season", "Summer")
    style = prompt_inputs.get("style", "Streetwear")
    demographic = prompt_inputs.get("demographic", "Gen Z")
    price_range = prompt_inputs.get("price_range", "Mid-range")
    gender = prompt_inputs.get("gender", "Unisex")
    region = prompt_inputs.get("region", "Coimbatore")

    style_notes = STYLE_GUIDE.get(style, STYLE_GUIDE["Casual"])

    palette_map = {
        "Summer": ["Powder Blue", "Soft White", "Stone Beige"],
        "Winter": ["Olive Brown", "Charcoal", "Warm Sand"],
        "Spring": ["Mint Grey", "Soft Peach", "Cloud White"],
        "Autumn": ["Rust Beige", "Muted Olive", "Warm Taupe"]
    }

    return {
        "design_name": f"{season} {style} Edit",
        "concept": (
            f"A {season.lower()}-ready {style.lower()} outfit concept for {demographic.lower()} "
            f"{gender.lower()} shoppers in {region}, balancing trend relevance, comfort, "
            f"and {price_range.lower()} market practicality."
        ),
        "colors": palette_map.get(season, ["Soft White", "Stone Beige", "Slate"]),
        "fabrics": FABRIC_GUIDE.get(season, ["Cotton", "Linen"])[:2],
        "size_recommendation": SIZE_GUIDE.get(demographic, "S to XL with balanced fits"),
        "production_feasibility": "High feasibility with low-to-medium construction complexity and locally sourceable materials.",
        "target_demographic": f"{demographic} fashion shoppers",
        "suggested_features": FEATURE_SUGGESTIONS.get(season, FEATURE_SUGGESTIONS["Summer"]),
        "style_notes": style_notes,
        "system_status": "Demo mode active - add GROQ_API_KEY in Streamlit secrets to enable live AI generation."
    }


def generate_outfit_reference_images(season: str, style: str, demographic: str, gender: str) -> List[Dict[str, str]]:
    queries = [
        f"{season.lower()} {style.lower()} outfit {gender.lower()} fashion",
        f"{demographic.lower()} fashion outfit inspiration",
        f"editorial {style.lower()} fashion full body"
    ]

    refs = []
    for i, q in enumerate(queries, start=1):
        refs.append({
            "url": f"https://picsum.photos/seed/trendweave-fashion-{urllib.parse.quote(q)}/{900}/{700}",
            "caption": q.title()
        })
    return refs


def normalize_ai_result(parsed: Dict, prompt_inputs: Dict[str, str]) -> Dict:
    fallback = demo_result(prompt_inputs)

    result = {
        "design_name": parsed.get("design_name", fallback["design_name"]),
        "concept": parsed.get("concept", fallback["concept"]),
        "colors": parsed.get("colors", fallback["colors"]),
        "fabrics": parsed.get("fabrics", fallback["fabrics"]),
        "size_recommendation": parsed.get("size_recommendation", fallback["size_recommendation"]),
        "production_feasibility": parsed.get("production_feasibility", fallback["production_feasibility"]),
        "target_demographic": parsed.get("target_demographic", fallback["target_demographic"]),
        "suggested_features": parsed.get("suggested_features", fallback["suggested_features"]),
        "style_notes": parsed.get("style_notes", fallback["style_notes"]),
        "system_status": "Success - Groq JSON mode"
    }

    if not isinstance(result["colors"], list):
        result["colors"] = [safe_str(result["colors"])]
    if not isinstance(result["fabrics"], list):
        result["fabrics"] = [safe_str(result["fabrics"])]
    if not isinstance(result["suggested_features"], list):
        result["suggested_features"] = [safe_str(result["suggested_features"])]
    if not isinstance(result["style_notes"], list):
        result["style_notes"] = [safe_str(result["style_notes"])]

    result["colors"] = [safe_str(x) for x in result["colors"]][:3]
    result["fabrics"] = [safe_str(x) for x in result["fabrics"]][:2]
    result["suggested_features"] = [safe_str(x) for x in result["suggested_features"]][:3]
    result["style_notes"] = [safe_str(x) for x in result["style_notes"]][:3]

    return result


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

        if response.status_code != 200:
            data = demo_result(prompt_inputs)
            try:
                result = response.json()
                data["system_status"] = f"Groq fallback triggered - HTTP {response.status_code}: {result}"
            except Exception:
                data["system_status"] = f"Groq fallback triggered - HTTP {response.status_code}"
            return data

        result = response.json()
        content = result["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return normalize_ai_result(parsed, prompt_inputs)

    except Exception as e:
        data = demo_result(prompt_inputs)
        data["system_status"] = f"Groq fallback triggered: {str(e)}"
        return data


load_css()

st.markdown(
    """
    <div class="main-shell">
        <div class="hero-title">TrendWeave AI</div>
        <div class="hero-subtitle">
            Fashion design intelligence for generating outfit concepts using trend signals,
            season, demographic preference, weather context, and production-aware material guidance.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Design Configuration</div>', unsafe_allow_html=True)

with st.form("fashion_form"):
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        demographic = st.selectbox("Target Demographic", ["Gen Z", "Working Professionals", "Teens", "Adults"])
    with c2:
        gender = st.selectbox("Gender Segment", ["Women", "Men", "Unisex"])
    with c3:
        season = st.selectbox("Season", ["Summer", "Winter", "Spring", "Autumn"])

    c4, c5, c6 = st.columns(3, gap="medium")
    with c4:
        region = st.text_input("Region / City", "Coimbatore")
    with c5:
        style = st.selectbox("Style Preference", ["Streetwear", "Minimal", "Casual", "Ethnic Fusion", "Formal"])
    with c6:
        price_range = st.selectbox("Price Range", ["Budget", "Mid-range", "Premium"])

    generate = st.form_submit_button("Generate Fashion Design")

st.markdown('</div>', unsafe_allow_html=True)

weather = get_weather(region.strip()) if region.strip() else None
temp_text = f"{weather['temperature']}°C" if weather else "Unavailable"
wind_text = f"{weather['wind_speed']} km/h" if weather else "Unavailable"

m1, m2, m3 = st.columns(3, gap="medium")
with m1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Selected Season</div>
            <div class="metric-value">{season}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with m2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Temperature Context</div>
            <div class="metric-value">{temp_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with m3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">AI Mode</div>
            <div class="metric-value">{'Groq Live' if GROQ_API_KEY else 'Demo'}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

if generate:
    clean_region = region.strip() if region.strip() else "Coimbatore"

    prompt_inputs = {
        "demographic": demographic,
        "gender": gender,
        "season": season,
        "region": clean_region,
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
Region: {clean_region}
Trend keywords: {', '.join(TREND_DATA[season])}
Suggested fabrics: {', '.join(FABRIC_GUIDE[season])}
Suggested sizes: {SIZE_GUIDE[demographic]}
Price range: {price_range}
Current weather: {temp_text}
Wind speed: {wind_text}
Need: one commercially realistic outfit concept suitable for a fashion design ideation tool.
"""

    with st.spinner("Generating fashion concept..."):
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

    left, right = st.columns(2, gap="medium")

    with left:
        st.markdown(
            f"""
            <div c
