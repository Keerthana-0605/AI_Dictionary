import streamlit as st
import requests
from urllib.parse import quote
from html import escape

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="AI Dictionary",
    page_icon="📚",
    layout="centered"
)

# ---------- DESIGN ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        135deg, #fff0f7, #fceafa, #eaf5ff
    );
    color: #25213A !important;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.stApp h1, .stApp h2, .stApp h3 {
    color: #7B2FE8 !important;
}

.stApp p, .stApp li, .stApp label,
[data-testid="stMarkdownContainer"] p {
    color: #25213A !important;
}

.stTextInput input {
    background-color: #FFFFFF !important;
    color: #25213A !important;
    -webkit-text-fill-color: #25213A !important;
    border: 2px solid #8B5CF6 !important;
    border-radius: 14px !important;
}

.stButton > button {
    background: linear-gradient(
        90deg, #7628DF, #E32383
    ) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.7rem !important;
}

.stButton > button p {
    color: #FFFFFF !important;
}

.result-card {
    background: rgba(255,255,255,0.88);
    border: 1px solid #E5D3FA;
    border-radius: 14px;
    padding: 16px;
    margin: 12px 0;
    overflow-wrap: anywhere;
    color: #25213A !important;
}

.result-card p {
    color: #25213A !important;
}

.word-title {
    color: #7B2FE8 !important;
    font-size: 2rem;
    font-weight: bold;
}

.footer {
    color: #7138B5 !important;
    text-align: center;
    margin-top: 30px;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown(
    "<h1 style='text-align:center;'>📚 AI Dictionary</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;'>"
    "Discover the meaning of any word ✨"
    "</p>",
    unsafe_allow_html=True
)

# ---------- INPUT ----------
word = st.text_input(
    "Enter a word",
    placeholder="Example: World, Love, Happiness..."
)

# ---------- DICTIONARY FUNCTION ----------
def get_definition(word):
    url = (
        "https://api.dictionaryapi.dev/api/v2/entries/en/"
        + quote(word.strip())
    )

    response = requests.get(url, timeout=20)

    if response.status_code == 404:
        return [], "Word not found. Please check the spelling."

    response.raise_for_status()
    data = response.json()

    results = []

    for entry in data:
        for meaning in entry.get("meanings", []):
            part_of_speech = meaning.get(
                "partOfSpeech", "Unknown"
            )

            for definition in meaning.get("definitions", []):
                text = definition.get("definition", "")

                if text:
                    results.append({
                        "part_of_speech": part_of_speech,
                        "definition": text,
                        "example": definition.get("example", "")
                    })

    return results, None


# ---------- SEARCH ----------
if st.button("Find Meaning ✨", use_container_width=True):
    # Clear previous results before a new search
    st.session_state.pop("results", None)
    st.session_state.pop("searched_word", None)

    if not word.strip():
        st.warning("Please enter a word first.")
    else:
        try:
            with st.spinner("Finding the meaning... ✨"):
                results, error = get_definition(word)

            if error:
                st.warning(error)
            elif not results:
                st.warning("No definitions found.")
            else:
                st.session_state["results"] = results
                st.session_state["searched_word"] = word.strip()

        except requests.exceptions.Timeout:
            st.error("The request timed out. Please try again.")

        except requests.exceptions.RequestException:
            st.error(
                "Unable to connect to the English dictionary. "
                "Check your internet connection and try again."
            )

        except (ValueError, TypeError, KeyError):
            st.error("Something went wrong. Please try again.")

# ---------- DISPLAY RESULTS ----------
if "results" in st.session_state:
    safe_word = escape(st.session_state["searched_word"])

    st.markdown(
        f"<div class='word-title'>{safe_word}</div>",
        unsafe_allow_html=True
    )

    st.caption("Definitions in English")

    for index, item in enumerate(
        st.session_state["results"], start=1
    ):
        pos = escape(item["part_of_speech"])
        definition = escape(item["definition"])

        st.markdown(
            f"""
            <div class="result-card">
                <p><strong>POS:</strong> {pos}</p>
                <p><strong>Meaning {index}:</strong>
                {definition}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if item["example"]:
            example = escape(item["example"])
            st.markdown(
                f"""
                <div class="result-card">
                    <p><strong>Example:</strong> {example}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

# ---------- FOOTER ----------
st.markdown(
    """
    <div class="footer">
        Made with ❤️ using Python & Streamlit
        <br>
        Your little dictionary, anytime, anywhere ✨
    </div>
    """,
    unsafe_allow_html=True
)
