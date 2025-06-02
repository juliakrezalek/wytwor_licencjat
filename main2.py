from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_prompt(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def chat():
    prompt = load_prompt("chatbot2.md")
    print("Rozpoczynasz rozmowę z Chatbotem 2\n")

    messages = [{"role": "system", "content": prompt}]

    while True:
        user_input = input("Ty: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})

        print(f"Chatbot: {reply}\n")


if __name__ == "__main__":
    chat()