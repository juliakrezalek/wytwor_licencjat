import gradio as gr
import os
from dotenv import load_dotenv
from openai import OpenAI

# Załaduj klucz API
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Wczytaj prompt systemowy z pliku .md
def load_prompt(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

system_prompt = load_prompt("chatbot1_ekspert.md")

# Pamięć rozmowy
chat_history = []

def respond(user_input, history):
    if not user_input.strip():
        return "", history
    
    messages = [{"role": "system", "content": system_prompt}]
    for human, bot in history:
        messages.append({"role": "user", "content": human})
        messages.append({"role": "assistant", "content": bot})
    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o",  # lub gpt-4-turbo
        messages=messages,
        temperature=0.7,
    )
    reply = response.choices[0].message.content
    history.append((user_input, reply))
    return "", history

def export_history(history):
    text = "\n\n".join([f"Ty: {user}\nChatbot: {bot}" for user, bot in history])
    return text

with gr.Blocks(title="Badanie") as demo:
    gr.Markdown("## 🩺 Analiza przypadku medycznego")
    chatbot = gr.Chatbot(label="Chatbot Ekspert")
    with gr.Row():
        msg = gr.Textbox(placeholder="Wpisz swoją wiadomość...", label="Twoja wiadomość", scale=5)
        clear = gr.Button("🗑️ Wyczyść", variant="secondary")
        export = gr.Button("💾 Eksportuj rozmowę", variant="primary")

    # Ukryty komponent na potrzeby eksportu
    txt_file = gr.File(label="Plik rozmowy", visible=False)

    # Reakcja na wpis
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)
    export.click(fn=export_history, inputs=chatbot, outputs=txt_file)

demo.launch()

