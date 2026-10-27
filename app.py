
import streamlit as st
import requests
import re
from html import unescape
from collections import defaultdict

# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="WordBloom Dictionary",
    page_icon="📚",
    layout="centered"
)

# ---------------- COLORFUL WEBPAGE DESIGN ----------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        135deg,
        #F5EFFF 0%,
        #FFF0F6 50%,
        #E8F7FF 100%
    );
}

.block-container {
    max-width: 850px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1 {
    color: #6D28D9 !important;
    text-align: center;
    font-size: 2.7rem !important;
    font-weight: 800 !important;
}

.stTextInput label {
    color: #6D28D9 !important;
    font-weight: 600;
}

.stTextInput input {
    background-color: #FFFFFF;
    border: 2px solid #C4B5FD;
    border-radius: 12px;
    color: #312E81;
}

.stTextInput input:focus {
    border-color: #A855F7;
    box-shadow: 0 0 0 2px #E9D5FF;
}

.stButton > button {
    background: linear-gradient(
        90deg,
        #7C3AED,
        #EC4899
    );
    color: white !important;
    border: none;
    border-radius: 12px;
    padding: 0.65rem 1.5rem;
    font-weight: 700;
    width: 100%;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background: linear-gradient(
        90deg,
        #6D28D9,
        #DB2777
    );
    transform: translateY(-2px);
    box-shadow: 0 5px 15px #C4B5FD;
}

h2, h3 {
    color: #7C3AED !important;
}

div[data-testid="stMarkdownContainer"] {
    line-height: 1.7;
}

header[data-testid="stHeader"] {
    background: transparent;
}
</style>
""", unsafe_allow_html=True)

# ---------------- PAGE TITLE ----------------

st.markdown(
    "<h1>📚 AI Dictionary</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center; color:#7C3AED;'>"
    "Discover the meaning of any word ✨"
    "</p>",
    unsafe_allow_html=True
)

# ---------------- DICTIONARY SOURCE 1 ----------------

def free_dictionary(word):
    url = (
        "https://api.dictionaryapi.dev/api/v2/entries/en/"
        + requests.utils.quote(word)
    )

    response = requests.get(url, timeout=15)

    if response.status_code != 200:
        return []

    results = []

    for entry in response.json():
        for meaning in entry.get("meanings", []):
            pos = meaning.get("partOfSpeech", "Unknown")

            for item in meaning.get("definitions", []):
                definition = item.get("definition", "").strip()

                if definition:
                    results.append((pos, definition))

    return results

# ---------------- DICTIONARY SOURCE 2 ----------------

def clean_text(text):
    text = re.sub(r"<[^>]+>", "", text)
    return unescape(text).strip()


def wiktionary(word):
    url = (
        "https://en.wiktionary.org/api/rest_v1/page/definition/"
        + requests.utils.quote(word)
    )

    response = requests.get(
        url,
        headers={"User-Agent": "AI Dictionary/1.0"},
        timeout=15
    )

    if response.status_code != 200:
        return []

    data = response.json()
    results = []

    for item in data.get("en", []):
        pos = item.get("partOfSpeech", "Unknown")

        for definition in item.get("definitions", []):
            definition_text = clean_text(
                definition.get("definition", "")
            )

            if definition_text:
                results.append((pos, definition_text))

    return results

# ---------------- WORD INPUT ----------------

word = st.text_input(
    "Enter a word",
    placeholder="e.g. beautiful, elephant, extraordinary"
)

if st.button("Find Meaning ✨"):

    word = word.strip()

    if not word:
        st.warning("Please enter a word.")

    else:
        try:
            with st.spinner("Finding meanings..."):

                # Try the first dictionary
                results = free_dictionary(word.lower())

                # Use the second source if the first returns no results
                if not results:
                    results = wiktionary(word.lower())

            if results:

                # Group definitions by part of speech
                grouped = defaultdict(list)
                seen = set()

                for pos, definition in results:

                    pos_key = pos.strip().lower()
                    definition = definition.strip()
                    definition_key = definition.lower()

                    key = (pos_key, definition_key)

                    if definition and key not in seen:
                        seen.add(key)

                        if pos_key not in grouped:
                            grouped[pos_key] = {
                                "pos": pos.strip(),
                                "definitions": []
                            }

                        grouped[pos_key]["definitions"].append(
                            definition
                        )

                # Display only the word, POS, and meanings
                st.subheader(word)

                for item in grouped.values():

                    st.markdown(
                        f"**POS:** {item['pos']}"
                    )

                    for definition in item["definitions"]:
                        st.markdown(
                            f"**Meaning:** {definition}"
                        )

            else:
                st.error("Meaning not found for this word.")

        except requests.RequestException:
            st.error(
                "Unable to connect. Please check your internet connection."
            )

        except (ValueError, KeyError, TypeError):
            st.error("Unable to read the dictionary results.")
