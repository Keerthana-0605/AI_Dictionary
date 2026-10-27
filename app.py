import streamlit as st
import requests
from urllib.parse import quote

st.set_page_config(
    page_title="AI Dictionary",
    page_icon="📚",
    layout="centered"
)

# ---------- DESIGN ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #fff0f7, #fceafa, #eaf5ff);
    color: #25213A !important;
}
.main .block-container {
    padding-top: 2rem;
}
.stApp h1, .stApp h2, .stApp h3 {
    color: #7B2FE8 !important;
}
.stApp p, .stApp li, .stApp label,
[data-testid="stMarkdownContainer"] p {
    color: #25213A !important;
}
.stTextInput input {
    background: white !important;
    color: #25213A !important;
    -webkit-text-fill-color: #25213A !important;
    border: 2px solid #8B5CF6 !important;
    border-radius: 14px !important;
}
.stButton > button {
    background: linear-gradient(90deg, #7628DF, #E32383) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
}
.stButton > button p {
    color: white !important;
}
.result-card {
    background: rgba(255,255,255,0.85);
    border: 1px solid #E5D3FA;
    border-radius: 14px;
    padding: 16px;
    margin: 12px 0;
    overflow-wrap: anywhere;
    color: #25213A !important;
}
.result-card p, .result-card strong {
    color: #25213A !important;
}
.word-title {
    color: #7B2FE8 !important;
    font-size: 2rem;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown(
    "<h1 style='text-align:center'>📚 AI Dictionary</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center'>Discover the meaning of any word ✨</p>",
    unsafe_allow_html=True
)

# ---------- LANGUAGE ----------
language = st.selectbox(
    "Choose meaning language / అర్థం భాషను ఎంచుకోండి",
    ["English", "Telugu (తెలుగు)"]
)

word = st.text_input(
    "Enter a word",
    placeholder="Example: World, Love, Happiness"
)


# ---------- ENGLISH DICTIONARY ----------
def get_definition(word):
    url = (
        "https://api.dictionaryapi.dev/api/v2/entries/en/"
        + quote(word.strip())
    )

    response = requests.get(url, timeout=15)
    response.raise_for_status()
    data = response.json()

    results = []

    for entry in data:
        for meaning in entry.get("meanings", []):
            for definition in meaning.get("definitions", []):
                text = definition.get("definition", "")

                if text:
                    results.append({
                        "part_of_speech": meaning.get(
                            "partOfSpeech", "Unknown"
                        ),
                        "definition": text,
                        "example": definition.get("example", "")
                    })

    return results


# ---------- ENGLISH TO TELUGU TRANSLATION ----------
def translate_to_telugu(text):
    if not text or not text.strip():
        return ""

    # MyMemory accepts up to 500 bytes per request.
    # Split longer definitions into smaller chunks.
    words = text.split()
    chunks = []
    current = ""

    for word_part in words:
        candidate = (current + " " + word_part).strip()

        if len(candidate.encode("utf-8")) > 450:
            if current:
                chunks.append(current)
            current = word_part
        else:
            current = candidate

    if current:
        chunks.append(current)

    translated_chunks = []

    for chunk in chunks:
        response = requests.get(
            "https://api.mymemory.translated.net/get",
            params={
                "q": chunk,
                "langpair": "en|te"
            },
            timeout=20
        )
        response.raise_for_status()
        data = response.json()

        translated = data.get(
            "responseData", {}
        ).get("translatedText", "")

        if (
            data.get("responseStatus") != 200
            or not translated
            or data.get("quotaFinished") is True
        ):
            raise ValueError(
                data.get("responseDetails")
                or "Translation service did not return a translation."
            )

        translated_chunks.append(translated)

    return " ".join(translated_chunks)


# ---------- SEARCH ----------
if st.button("Find Meaning ✨", use_container_width=True):
    if not word.strip():
        st.warning("Please enter a word first.")
    else:
        try:
            with st.spinner("Finding the meaning... ✨"):
                results = get_definition(word)

                if not results:
                    st.warning("No definitions found. Check the spelling.")
                    st.stop()

                # Translate definitions when Telugu is selected.
                if language == "Telugu (తెలుగు)":
                    for item in results:
                        item["definition"] = translate_to_telugu(
                            item["definition"]
                        )

                        if item["example"]:
                            item["example"] = translate_to_telugu(
                                item["example"]
                            )

            st.session_state["results"] = results
            st.session_state["searched_word"] = word.strip()
            st.session_state["result_language"] = language

        except requests.exceptions.Timeout:
            st.error("The request timed out. Please try again.")
        except requests.exceptions.RequestException:
            st.error(
                "Could not connect to a dictionary or translation service. "
                "Please check your internet and try again."
            )
        except (ValueError, KeyError) as error:
            st.error(
                "Telugu translation failed. The translation service may "
                "be unavailable or its free quota may be exhausted. "
                f"Details: {error}"
            )

# ---------- DISPLAY RESULTS ----------
if "results" in st.session_state:
    st.markdown(
        f"<div class='word-title'>"
        f"{st.session_state['searched_word']}</div>",
        unsafe_allow_html=True
    )

    if st.session_state["result_language"] == "Telugu (తెలుగు)":
        st.write("అర్థాలు తెలుగులో")
    else:
        st.write("Definitions in English")

    for index, item in enumerate(st.session_state["results"], 1):
        st.markdown(
            f"""
            <div class="result-card">
                <p><strong>POS:</strong>
                {item['part_of_speech']}</p>
                <p><strong>Meaning {index}:</strong>
                {item['definition']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if item["example"]:
            st.markdown(
                f"""
                <div class="result-card">
                    <p><strong>Example:</strong>
                    {item['example']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

st.markdown(
    "<p style='text-align:center'>Made with ❤️ using Python & Streamlit</p>",
    unsafe_allow_html=True
)
