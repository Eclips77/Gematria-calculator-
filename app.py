import streamlit as st
import unicodedata
import pandas as pd
import time
from collections import Counter

# -----------------------------------------------------------------------------
# 1. CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Gematria Calculator • חשבון גימטריה",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for colors, fonts, and RTL support
st.markdown("""
<style>
    /* Global fonts */
    @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;700&family=Roboto:wght@400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Roboto', 'Heebo', sans-serif;
    }

    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        font-size: 3rem !important;
        font-weight: 700;
    }

    /* Hebrew Theme Colors */
    .hebrew-metric {
        color: #1E3A8A; /* Deep Blue */
    }

    /* English Theme Colors */
    .english-metric {
        color: #D97706; /* Gold */
    }

    /* Text Area font size */
    .stTextArea textarea {
        font-size: 1.2rem;
    }

    /* RTL Class for Hebrew Input/Output */
    .rtl {
        direction: rtl;
        text-align: right;
    }

    /* Copy Button Styling workaround */
    .stButton button {
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. CONSTANTS & DATA STRUCTURES
# -----------------------------------------------------------------------------

HEBREW_VALUES = {
    'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9, 'י': 10,
    'כ': 20, 'ך': 20, 'ל': 30, 'מ': 40, 'ם': 40, 'נ': 50, 'ן': 50, 'ס': 60, 'ע': 70,
    'פ': 80, 'ף': 80, 'צ': 90, 'ץ': 90, 'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400
}

ENGLISH_ORDINAL = {chr(ord('a') + i): i+1 for i in range(26)}
ENGLISH_REDUCTION = {chr(ord('a') + i): (i % 9) + 1 for i in range(26)}
ENGLISH_REVERSE_ORDINAL = {chr(ord('a') + i): 26 - i for i in range(26)}
ENGLISH_REVERSE_REDUCTION = {chr(ord('a') + i): ((25 - i) % 9) + 1 for i in range(26)}


# -----------------------------------------------------------------------------
# 3. COMPUTATION LOGIC
# -----------------------------------------------------------------------------

def compute_hebrew_gematria(text):
    if not text:
        return {"Standard": 0, "Mispar Katan": 0, "Letters": 0, "Words": 0}, []

    normalized_text = unicodedata.normalize('NFKD', text)
    clean_chars = []
    clean_values = []

    for char in normalized_text:
        if char in HEBREW_VALUES:
            val = HEBREW_VALUES[char]
            clean_chars.append(char)
            clean_values.append(val)

    if not clean_chars:
        return {"Standard": 0, "Mispar Katan": 0, "Letters": 0, "Words": len(text.split())}, []

    total_standard = sum(clean_values)
    total_katan = sum((v - 1) % 9 + 1 for v in clean_values)

    results = {
        "Standard": total_standard,
        "Mispar Katan": total_katan,
        "Letters": len(clean_chars),
        "Words": len(text.split())
    }

    breakdown = []
    for c, v in zip(clean_chars, clean_values):
        breakdown.append({"Letter": c, "Value": v, "Small": (v - 1) % 9 + 1})

    return results, breakdown

def compute_english_gematria(text):
    if not text:
        return {}, []

    # Filter only characters that exist in our English map (a-z)
    # This prevents KeyErrors if user enters Hebrew/foreign chars in English mode
    clean_text = [c.lower() for c in text if c.lower() in ENGLISH_ORDINAL]

    if not clean_text:
        return {}, []

    ordinal = sum(ENGLISH_ORDINAL[c] for c in clean_text)
    reduction = sum(ENGLISH_REDUCTION[c] for c in clean_text)
    rev_ordinal = sum(ENGLISH_REVERSE_ORDINAL[c] for c in clean_text)
    rev_reduction = sum(ENGLISH_REVERSE_REDUCTION[c] for c in clean_text)

    results = {
        "English Ordinal": ordinal,
        "Full Reduction": reduction,
        "Reverse Ordinal": rev_ordinal,
        "Reverse Reduction": rev_reduction
    }

    breakdown = []
    for c in clean_text:
        breakdown.append({
            "Letter": c.upper(),
            "Ordinal": ENGLISH_ORDINAL[c],
            "Reduction": ENGLISH_REDUCTION[c],
            "Rev. Ordinal": ENGLISH_REVERSE_ORDINAL[c],
            "Rev. Reduction": ENGLISH_REVERSE_REDUCTION[c]
        })

    return results, breakdown

# -----------------------------------------------------------------------------
# 4. UI STRUCTURE
# -----------------------------------------------------------------------------

# Initialize Session State
if 'history' not in st.session_state:
    st.session_state['history'] = []

# URL Parameters Handling
query_params = st.query_params
default_lang_idx = 0
default_text = ""

if "lang" in query_params:
    lang_param = query_params["lang"]
    if lang_param == "english":
        default_lang_idx = 1
    elif lang_param == "hebrew":
        default_lang_idx = 0

if "text" in query_params:
    default_text = query_params["text"]

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    language = st.selectbox("Language", ["Hebrew 🇮🇱", "English 🇺🇸"], index=default_lang_idx)

    st.markdown("---")
    st.markdown("### About")
    st.info(
        "**Gematria Calculator**\n\n"
        "Compute values instantly using standard Hebrew and English methods.\n\n"
        "**Hebrew**: Standard (Mispar Gadol, finals=regular).\n"
        "**English**: Ordinal, Reduction, Reverse."
    )
    theme_toggle = st.toggle("Dark Mode Preview (Fake)", value=True, disabled=True, help="Streamlit handles themes automatically.")

# Main Header
if "Hebrew" in language:
    title = "🧮 Gematria Calculator • חשבון גימטריה"
    input_placeholder = "הקלד מילה או ביטוי כאן... (למשל: בראשית ברא)"
    is_hebrew = True
    primary_color_cls = "hebrew-metric"
    direction = "rtl"
    lang_key = "hebrew"
else:
    title = "🧮 Gematria Calculator"
    input_placeholder = "Enter word or phrase here... (e.g., Hello World)"
    is_hebrew = False
    primary_color_cls = "english-metric"
    direction = "ltr"
    lang_key = "english"

st.markdown(f"<h1 style='text-align: center; background: -webkit-linear-gradient(45deg, #1E3A8A, #D97706); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>{title}</h1>", unsafe_allow_html=True)

# Input Section
input_container = st.container()
with input_container:
    input_text = st.text_area(
        "Input Text",
        value=default_text,
        height=150,
        placeholder=input_placeholder,
        label_visibility="collapsed",
        help="Enter text to calculate."
    )
    st.caption(f"Character Count: {len(input_text)}")

# Calculate Action
if st.button("🧮 Calculate Gematria", use_container_width=True, type="primary"):
    # Update URL params
    st.query_params["lang"] = lang_key
    st.query_params["text"] = input_text

    with st.spinner("Calculating..."):
        time.sleep(0.1)

        if is_hebrew:
            results, breakdown_data = compute_hebrew_gematria(input_text)
            st.markdown("---")
            c1, c2, c3, c4 = st.columns(4)

            def colored_metric(col, label, value, icon):
                col.markdown(f"""
                <div style="text-align: center;" class="{direction}">
                    <span style="font-size: 1rem; color: #888;">{label}</span><br>
                    <span style="font-size: 2.5rem; font-weight: bold;" class="{primary_color_cls}">{value}</span>
                    <div style="font-size: 1.5rem;">{icon}</div>
                </div>
                """, unsafe_allow_html=True)
                # Copy button workaround
                if value > 0:
                   col.code(str(value), language="text")

            colored_metric(c1, "Standard (Ragil)", results.get("Standard", 0), "✡️")
            colored_metric(c2, "Mispar Katan", results.get("Mispar Katan", 0), "🔢")
            colored_metric(c3, "Letter Count", results.get("Letters", 0), "📝")
            colored_metric(c4, "Word Count", results.get("Words", 0), "📑")

        else:
            results, breakdown_data = compute_english_gematria(input_text)
            st.markdown("---")
            c1, c2, c3, c4 = st.columns(4)

            def gold_metric(col, label, value):
                col.markdown(f"""
                <div style="text-align: center;">
                    <span style="font-size: 1rem; color: #888;">{label}</span><br>
                    <span style="font-size: 2.5rem; font-weight: bold; color: #D97706;">{value}</span>
                    <div style="font-size: 1.5rem;">📜</div>
                </div>
                """, unsafe_allow_html=True)
                if value is not None and value > 0:
                    col.code(str(value), language="text")

            if results:
                gold_metric(c1, "English Ordinal", results["English Ordinal"])
                gold_metric(c2, "Full Reduction", results["Full Reduction"])
                gold_metric(c3, "Reverse Ordinal", results["Reverse Ordinal"])
                gold_metric(c4, "Rev. Reduction", results["Reverse Reduction"])
            else:
                st.warning("No valid English letters found.")

        # Breakdown Expander
        if breakdown_data:
            with st.expander("🔍 Letter Breakdown", expanded=False):
                df = pd.DataFrame(breakdown_data)
                st.dataframe(df, use_container_width=True)

        # Update History
        if input_text.strip():
            entry = {
                "text": input_text[:30] + "..." if len(input_text) > 30 else input_text,
                "lang": "Hebrew" if is_hebrew else "English",
                "val": results.get("Standard", 0) if is_hebrew else results.get("English Ordinal", 0)
            }
            st.session_state['history'].insert(0, entry)
            st.session_state['history'] = st.session_state['history'][:5]

# History Section
if st.session_state['history']:
    st.markdown("---")
    st.markdown("### 🕒 Recent Calculations")
    hist_cols = st.columns(5)
    for i, item in enumerate(st.session_state['history']):
        with hist_cols[i]:
            st.caption(f"{item['lang']}")
            st.text(f"{item['text']}")
            st.markdown(f"**{item['val']}**")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: grey;'>"
    "Built with ❤️ using Streamlit | Gematria Calculator v1.0"
    "</div>",
    unsafe_allow_html=True
)
