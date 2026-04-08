import streamlit as st
import requests
import json
import urllib.parse
from typing import Dict, List, Optional

st.set_page_config(
    page_title="TrendWeave AI",
    page_icon="âœ¨",
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

if "generated" not in st.session_state:
    st.session_state.generated = False
if "result" not in st.session_state:
    st.session_state.result = None
if "refs" not in st.session_state:
    st.session_state.refs = []
if "submitted_inputs" not in st.session_state:
    st.session_state.submitted_inputs = {}


def load_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            --bg: #f6f7fb;
            --surface: #ffffff;
            --surface-soft: #f8fafc;
            --border: #e5e7eb;
            --text: #0f172a;
            --muted: #475569;
            --soft: #64748b;
            --primary: #1d4ed8;
            --primary-soft: #dbeafe;
            --radius: 18px;
            --shadow: 0 8px 30px rgba(15, 23, 42, 0.06);
        }

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
            color: var(--text);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 2.2rem;
            padding-bottom: 2.2rem;
            padding-left: 1.4rem;
            padding-right: 1.4rem;
        }

        section[data-testid="stSidebar"],
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"],
        div[data-testid="stStatusWidget"],
        #MainMenu,
        header,
        footer {
            visibility: hidden;
            height: 0;
            position: fixed;
        }

        .app-shell {
            background: transparent;
        }

        .hero-clean {
            background: transparent;
            border-bottom: 1px solid var(--border);
            padding: 0 0 1.5rem 0;
            margin-bottom: 1.6rem;
        }

        .app-title {
            color: var(--text);
            font-size: 2.1rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            text-align: center;
            margin-bottom: 0.45rem;
        }

        .app-subtitle {
            max-width: 760px;
            margin: 0 auto;
            text-align: center;
            color: var(--muted);
            font-size: 1rem;
            line-height: 1.7;
        }

        .section-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 1.25rem;
            box-shadow: var(--shadow);
            margin-bottom: 1.25rem;
        }

        .mini-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1rem;
            box-shadow: var(--shadow);
            min-height: 118px;
        }

        .section-title {
            color: var(--text);
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }

        .metric-wrap {
            background: var(--surface-soft);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1rem;
            text-align: center;
            min-height: 92px;
        }

        .metric-label {
            color: var(--soft);
            font-size: 0.82rem;
            margin-bottom: 0.4rem;
        }

        .metric-value {
            color: var(--text);
            font-size: 1rem;
            font-weight: 700;
        }

        .card-title {
            color: var(--text);
            font-size: 1.06rem;
            font-weight: 700;
            margin-bottom: 0.7rem;
        }

        .card-text {
            color: var(--muted);
            font-size: 0.95rem;
            line-height: 1.7;
        }

        .chip {
            display: inline-block;
            padding: 0.42rem 0.78rem;
            border-radius: 999px;
            background: #f8fafc;
            border: 1px solid var(--border);
            color: #1e293b;
            font-size: 0.82rem;
            margin: 0.18rem;
        }

        .image-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 18px;
            overflow: hidden;
            box-shadow: var(--shadow);
        }

        .image-caption {
            padding: 0.85rem 1rem 1rem 1rem;
            color: var(--muted);
            font-size: 0.9rem;
            text-align: center;
        }

        .status-box {
            background: #f8fafc;
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1rem;
            color: #334155;
            font-family: monospace;
            font-size: 0.84rem;
            white-space: pre-wrap;
            word-break: break-word;
        }

        .stTextInput label, .stSelectbox label {
            color: var(--text) !important;
            font-weight: 600 !important;
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        .stTextInput > div > div,
        .stSelectbox > div > div {
            background: #ffffff !important;
            border: 1px solid var(--border) !important;
            border-radius: 14px !important;
            min-height: 46px;
        }

        input, textarea, [data-baseweb="input"] input {
            color: var(--text) !important;
            -webkit-text-fill-color: var(--text) !important;
            caret-color: var(--text) !important;
            font-size: 15px !important;
        }

        .stButton > button,
        .stFormSubmitButton > button {
            width: 100%;
            border-radius: 14px;
            padding: 0.78rem 1rem;
            font-size: 0.98rem;
            font-weight: 700;
            border: 1px solid #1d4ed8;
            background: #1d4ed8;
            color: #ffffff;
            box-shadow: none;
        }

        .stMarkdown h2 {
            color: var(--text);
            font-size: 1.3rem;
            margin-top: 0.25rem;
            margin-bottom: 1rem;
        }

        ul {
            margin-top: 0.35rem;
        }

        @media (max-width: 900px) {
            .app-title {
                font-size: 1.75rem;
            }

            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


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
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,wind_speed_10m"
        )
        weather_res = requests.get(weather_url, timeout=20)
        current = weather_res.json().get("current", {})
        return {
            "temperature": current.get("temperature_2m", "N/A"),
            "wind_speed": current.get("wind_speed_10m", "N/A"),
        }
    except Exception:
        return None


def demo_result(prompt_inputs: Dict[str, str]) -> Dict:
    season = prompt_inputs.get("season", "Summer")
    style = prompt_inputs.get("style", "Minimal")
    demographic = prompt_inputs.get("demographic", "Gen Z")
    return {
        "design_name": f"{season} {style} Studio Set",
        "concept": f"A clean {season.lower()} {style.lower()} outfit concept for {demographic.lower()} customers, focused on wearable silhouettes, soft color balance, and commercial feasibility for fashion retail presentation.",
        "colors": ["Soft White", "Stone Beige", "Powder Blue"],
        "fabrics": FABRIC_GUIDE[season][:2],
        "size_recommendation": SIZE_GUIDE[demographic],
        "production_feasibility": "High feasibility with commercially practical fabric sourcing and moderate stitching complexity.",
        "target_demographic": f"{demographic} fashion customers",
        "suggested_features": [
            "Layer-friendly silhouette",
            "Comfort-driven fit balance",
            "Retail-ready color coordination",
        ],
        "style_notes": [
            "Keep the look polished but easy to wear.",
            "Use a calm palette with one softer accent tone.",
            "Focus on shape clarity for presentation and catalog appeal.",
        ],
        "debug_error": "Demo mode active - add GROQ_API_KEY in Streamlit secrets to enable live generation.",
    }


def generate_outfit_reference_images(season: str, style: str, demographic: str, gender: str) -> List[Dict[str, str]]:
    queries = [
        f"{season.lower()} {style.lower()} outfit {gender.lower()} fashion photography",
        f"{demographic.lower()} outfit street style fashion photo",
        f"editorial full body outfit {style.lower()} fashion photography",
    ]
    refs = []
    for q in queries:
        encoded = urllib.parse.quote(q)
        refs.append({
            "url": f"https://source.unsplash.com/featured/1200x900/?{encoded}",
            "caption": q.title(),
        })
    return refs


def generate_design(prompt: str, prompt_inputs: Dict[str, str]) -> Dict:
    if not GROQ_API_KEY:
        return demo_result(prompt_inputs)

    api_url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    system_message = """
You are a professional fashion intelligence assistant.
Return only valid JSON in this exact schema:
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
- Concept must be concise and commercially realistic.
- Suggested features must be outfit or garment features, not app features.
- Use production-friendly fabrics and realistic colors.
- Output JSON only.
"""

    payload = {
        "model": GROQ_MODEL,
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
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

st.markdown('<div class="app-shell">', unsafe_allow_html=True)
st.markdown(
    """
    <div class="hero-clean">
        <div class="app-title">TrendWeave AI</div>
        <div class="app-subtitle">
            Generate cleaner fashion concepts using seasonal trends, target audience, regional weather,
            fabrics, sizing logic, and outfit-focused reference imagery.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Design Configuration</div>', unsafe_allow_html=True)

with st.form("fashion_form"):
    row1_col1, row1_col2, row1_col3 = st.columns(3, gap="medium")
    with row1_col1:
        demographic = st.selectbox("Target Demographic", ["Gen Z", "Working Professionals", "Teens", "Adults"])
    with row1_col2:
        gender = st.selectbox("Gender Segment", ["Women", "Men", "Unisex"])
    with row1_col3:
        season = st.selectbox("Season", ["Summer", "Winter", "Spring", "Autumn"])

    row2_col1, row2_col2, row2_col3 = st.columns(3, gap="medium")
    with row2_col1:
        region = st.text_input("Region / City", "Coimbatore")
    with row2_col2:
        style = st.selectbox("Style Preference", ["Streetwear", "Minimal", "Casual", "Ethnic Fusion", "Formal"])
    with row2_col3:
        price_range = st.selectbox("Price Range", ["Budget", "Mid-range", "Premium"])

    generate = st.form_submit_button("Generate Fashion Design")

st.markdown('</div>', unsafe_allow_html=True)

weather = get_weather(region)
temp_text = f"{weather['temperature']}Â°C" if weather else "Unavailable"
wind_text = f"{weather['wind_speed']} km/h" if weather else "Unavailable"

m1, m2, m3 = st.columns(3, gap="medium")
with m1:
    st.markdown(
        f"""
        <div class="metric-wrap">
            <div class="metric-label">Selected Season</div>
            <div class="metric-value">{season}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m2:
    st.markdown(
        f"""
        <div class="metric-wrap">
            <div class="metric-label">Temperature Context</div>
            <div class="metric-value">{temp_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m3:
    st.markdown(
        f"""
        <div class="metric-wrap">
            <div class="metric-label">AI Mode</div>
            <div class="metric-value">{'Groq Live' if GROQ_API_KEY else 'Demo'}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

if generate:
    prompt_inputs = {
        "demographic": demographic,
        "gender": gender,
        "season": season,
        "region": region,
        "style": style,
        "price_range": price_range,
        "temp_text": temp_text,
        "wind_text": wind_text,
    }

    prompt = f"""
Create one original fashion outfit design.
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
Need: a realistic, retail-friendly fashion outfit concept.
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

    left, right = st.columns(2, gap="medium")
    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-title">{result.get("design_name", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card-text">{result.get("concept", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="card-text"><b>Target Demographic:</b> {result.get("target_demographic", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card-text"><b>Size Recommendation:</b> {result.get("size_recommendation", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card-text"><b>Region:</b> {submitted.get("region", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Materials & Production</div>', unsafe_allow_html=True)
        colors = result.get("colors", [])
        fabrics = result.get("fabrics", [])
        colors = colors if isinstance(colors, list) else [str(colors)]
        fabrics = fabrics if isinstance(fabrics, list) else [str(fabrics)]
        st.markdown("**Color Palette**")
        st.markdown("".join([f'<span class="chip">{c}</span>' for c in colors]), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Fabric Suggestions**")
        st.markdown("".join([f'<span class="chip">{f}</span>' for f in fabrics]), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="card-text"><b>Production Feasibility:</b> {result.get("production_feasibility", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown('<div class="mini-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Suggested Features</div>', unsafe_allow_html=True)
        st.markdown("".join([f'<span class="chip">{item}</span>' for item in result.get("suggested_features", [])]), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="mini-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Styling Notes</div>', unsafe_allow_html=True)
        for note in result.get("style_notes", []):
            st.markdown(f'- {note}')
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="mini-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Weather Context</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card-text"><b>Season:</b> {submitted.get("season", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card-text"><b>Temperature:</b> {submitted.get("temp_text", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card-text"><b>Wind Speed:</b> {submitted.get("wind_text", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("## Reference Moodboard")
    im1, im2, im3 = st.columns(3, gap="medium")
    for col, item in zip([im1, im2, im3], refs):
        with col:
            st.markdown('<div class="image-card">', unsafe_allow_html=True)
            st.image(item["url"], width="stretch")
            st.markdown(f'<div class="image-caption">{item["caption"]}</div>', 
