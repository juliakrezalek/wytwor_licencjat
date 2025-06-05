import streamlit as st
from openai import OpenAI
import os
import time
import pandas as pd
from dotenv import load_dotenv

# === Ładowanie klucza API ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Wczytywanie promptu z pliku ===
def load_prompt(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

# === Ustawienia strony ===
st.set_page_config(page_title="🧠 Analiza drugiego przypadku medycznego", layout="wide")
st.title("🧠 Analiza drugiego przypadku medycznego")

# === Inicjalizacja sesji ===
if "messages" not in st.session_state:
    system_prompt = load_prompt("chatbot2.md")
    st.session_state.messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": "Cześć! Z jakim przypadkiem medycznym pracujemy? Jak mogę ci pomóc?"}
    ]
    st.session_state.start_time = None

# === Licznik czasu ===
if st.session_state.start_time:
    elapsed_time = int(time.time() - st.session_state.start_time)
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    st.info(f"⏱️ Czas rozmowy: {minutes} min {seconds} sek")

# === Wyświetlanie czatu ===
for msg in st.session_state.messages:
    if msg["role"] != "system":
        emoji = "👤" if msg["role"] == "user" else "🩺"
        with st.chat_message(msg["role"]):
            st.markdown(f"{emoji} {msg['content']}")

# === Pole do wpisywania wiadomości ===
user_input = st.chat_input("Wpisz wiadomość...", key="chatbot2_input")

# === Przetwarzanie wiadomości ===
if user_input:
    if st.session_state.start_time is None:
        st.session_state.start_time = time.time()

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(f"👤 {user_input}")

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
if st.button("📄 Eksportuj rozmowę do CSV"):
    df = pd.DataFrame([m for m in st.session_state.messages if m["role"] != "system"])
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"czat_{timestamp}.csv"
    df.to_csv(filename, index=False)
    with open(filename, "rb") as file:
        st.download_button(label="Pobierz plik CSV", data=file, file_name=filename, mime="text/csv")