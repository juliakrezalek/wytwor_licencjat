import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
import time

# === Konfiguracja i klient OpenAI ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Wczytywanie system promptu z pliku ===
def load_prompt(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

system_prompt = load_prompt("chatbot1_ekspert.md")

# === Konfiguracja strony ===
st.set_page_config(page_title="Analiza pierwszego przypadku medycznego", layout="wide")
st.markdown("<h1 class='chat-title'>🧠 Analiza pierwszego przypadku medycznego</h1>", unsafe_allow_html=True)

# === Inicjalizacja historii czatu ===
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": "Dzień dobry! Z jakim przypadkiem medycznym się zwracasz? Jakie objawy są już znane?"}
    ]
    st.session_state.start_time = None

user_input = st.chat_input("Wpisz wiadomość...")

if user_input:
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()  # zapisuje dokładny moment startu

if st.session_state.start_time:
    elapsed_time = int(time.time() - st.session_state.start_time)
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    st.info(f"⏱️ Czas rozmowy: {minutes} min {seconds} sek")

# === Wyświetlanie czatu ===
for msg in st.session_state.messages:
    if msg["role"] != "system":
        emoji = "💬" if msg["role"] == "user" else "🩺"
        with st.chat_message(msg["role"]):
            st.markdown(f"{emoji} {msg['content']}")

# === Pole do wpisania wiadomości ===
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(f"💬 {user_input}")

    # Odpowiedź modelu
    response = client.chat.completions.create(
        model="gpt-4",
        messages=st.session_state.messages,
        temperature=0.7
    )
    reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(f"🩺 {reply}")

# === Eksport do CSV ===
if st.button("💾 Eksportuj rozmowę do CSV"):
    df = pd.DataFrame([
        {"Rola": msg["role"], "Wiadomość": msg["content"]}
        for msg in st.session_state.messages if msg["role"] != "system"
    ])
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Pobierz plik CSV", data=csv, file_name="rozmowa_chatbot.csv", mime="text/csv")

# === Stylizacja ===
st.markdown("""
<style>
    .chat-title {
        font-size: 30px;
        font-weight: bold;
        color: #004080;
        text-align: center;
        margin-bottom: 30px;
    }
    .stTextInput > div > input {
        border: 2px solid #0055a5;
        border-radius: 30px;
        padding: 10px;
        font-size: 16px;
    }
    .stChatMessage {
        font-size: 16px;
        line-height: 1.6;
    }
    button[kind="primary"] {
        background-color: #0055a5;
        color: white;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)
