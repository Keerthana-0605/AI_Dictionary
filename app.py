import streamlit as st
import requests
import urllib.parse

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="AI Dictionary ✨",
    page_icon="📚",
    layout="centered"
)

# ---------------- CUSTOM DESIGN ----------------
st.markdown("""
<style>
/* App background */
.stApp {
    background: linear-gradient(
        135deg,
        #fff0f7 0%,
        #fceafa 50%,
        #eaf5ff 100%
    );
    color: #25213A !important;
}

/* Main content */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Headings */
.stApp h1,
.stApp h2,
.stApp h3 {
    color: #7B2FE8 !important;
}

/* Normal text and dictionary definitions */
.stApp p,
.stApp li,
.stApp label,
.stMarkdown,
.stMarkdown p,
.stMarkdown li,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    color: #25213A !important;
}

/* Word input */
.stTextInput input {
    background-color: #FFFFFF !important;
    color: #25213A !important;
    -webkit-text-fill-color: #25213A !important;
    border: 2px solid #8B5CF6 !important;
    border-radius: 14px !important;
}

/* Input label */
.stTextInput label {
    color: #7138B5 !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #7628DF, #E32383) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.7rem 1.2rem !important;
    font-weight: bold !important;
}

/* Force button text to remain white */
.stButton > button p,
.stButton > button span {
    color: #FFFFFF !important;
}

/* Result card */
.dictionary-card {
    background: rgba(255, 255, 255, 0.82);
    border: 1px solid #E5D3FA;
    border-radius: 16px;
    padding: 18px;
    margin: 12px 0;
    color: #25213A !important;
    overflow-wrap: anywhere;
}

/* All text inside result cards */
.dictionary-card p,
.dictionary-card div,
.dictionary-card span,
.dictionary-card li,
.dictionary-card strong {
    color: #25213A !important;
}

/* Word title */
.word-title {
    color: #7B2FE8 !important;
    font-size: 2rem;
    font-weight: 750;
    margin-bottom: 12px;
}

/* Footer */
.footer {
    color: #7138B5 !important;
    text-align: center;
    margin-top: 30px;
    font-size: 14px;
}

/* Mobile spacing */
@media (max-width: 600px) {
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .word-title {
        font-size: 1.7rem;
    }
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown(
    "<h1 style='text-align:center;'>📚 AI Dictionary</h1>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <p style='text-align:center; color:#7138B5 !important;
    font-size:18px;'>
    Discover the meaning of any word ✨
    </p>
    """,
    unsafe_allow_html=True
)

st.write("")

# ---------------- LANGUAGE SELECTION ----------------
language = st.selectbox(
    "Choose meaning language / అర్థం భాషను ఎంచుకోండి",
    ["English", "Telugu (తెలుగు)"]
)

# ---------------- WORD INPUT ----------------
word = st.text_input(
    "Enter a word",
    placeholder="Example: World, Love, Happiness..."
)

# ---------------- DICTIONARY FUNCTION ----------------
def get_definition(word, language):
    encoded_word = urllib.parse.quote(word.strip())

    url = (
        "https://api.dictionaryapi.dev/api/v2/entries/en/"
        + encoded_word
    )

    try:
        response = requests.get(url, timeout=15)

        if response.status_code != 200:
            return None, "Word not found. Please check the spelling."

        data = response.json()

        if not isinstance(data, list) or not data:
            return None, "No definition was found for this word."

        results = []

        for entry in data:
            for meaning in entry.get("meanings", []):
                part_of_speech = meaning.get(
                    "partOfSpeech", "Not available"
                )

                for definition in meaning.get("definitions", []):
                    item = {
                        "part_of_speech": part_of_speech,
                        "definition": definition.get(
                            "definition", ""
                        ),
                        "example": definition.get("example", "")
                    }

                    if item["definition"]:
                        results.append(item)

        if not results:
            return None, "No definitions are available for this word."

        # Telugu translations use MyMemory translation API.
        if language == "Telugu (తెలుగు)":
            for item in results:
                item["definition"] = translate_to_telugu(
                    item["definition"]
                )

                if item["example"]:
                    item["example"] = translate_to_telugu(
                        item["example"]
                    )

        return results, None

    except requests.exceptions.Timeout:
        return None, "The request timed out. Please try again."

    except requests.exceptions.RequestException:
        return None, "Unable to connect. Please check your internet."

    except (ValueError, TypeError, KeyError):
        return None, "Something went wrong while reading the definition."


# ---------------- TELUGU TRANSLATION ----------------
def translate_to_telugu(text):
    try:
        url = "https://api.mymemory.translated.net/get"

        response = requests.get(
            url,
            params={
                "q": text,
                "langpair": "en|te"
            },
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            translated = data.get(
                "responseData", {}
            ).get("translatedText")

            if translated:
                return translated

        return text

    except (requests.exceptions.RequestException, ValueError):
        return text


# ---------------- SEARCH BUTTON ----------------
if st.button("Find Meaning ✨", use_container_width=True):
    if not word.strip():
        st.warning("Please enter a word first.")
    else:
        with st.spinner("Finding the meaning... ✨"):
            results, error = get_definition(word, language)

        if error:
            st.error(error)
        else:
            st.session_state["dictionary_word"] = word.strip()
            st.session_state["dictionary_results"] = results
            st.session_state["dictionary_language"] = language

# ---------------- DISPLAY RESULTS ----------------
if "dictionary_results" in st.session_state:
    results = st.session_state["dictionary_results"]
    result_word = st.session_state["dictionary_word"]
    result_language = st.session_state["dictionary_language"]

    st.markdown(
        f"<div class='word-title'>{result_word}</div>",
        unsafe_allow_html=True
    )

    if result_language == "Telugu (తెలుగు)":
        st.caption("అర్థాలు తెలుగులో")
    else:
        st.caption("Definitions in English")

    for index, item in enumerate(results, start=1):
        st.markdown(
            f"""
            <div class="dictionary-card">
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
                <div class="dictionary-card">
                    <p><strong>Example:</strong>
                    {item['example']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

# ---------------- FOOTER ----------------
st.markdown(
    """
    <div class="footer">
        Made with ❤️ using Python and Streamlit
        <br>
        Your little dictionary, anytime, anywhere ✨
    </div>
    """,
    unsafe_allow_html=True
)
