from fastapi import FastAPI, Request
from openai import OpenAI
import os, json

app = FastAPI()

# ------------------------------
# Konstanten direkt im Code
# ------------------------------
PROJECT_BACKUP_FILE = "project_backup.json"
HTTP_REFERER = "https://roblox-plugin.example.com"
X_TITLE = "Roblox AI Plugin"

# ------------------------------
# OpenRouter Client (API Key aus Env)
# ------------------------------
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# ------------------------------
# Test-Endpoint
# ------------------------------
@app.get("/")
def home():
    return {"status": "ok"}

# ------------------------------
# Scan Endpoint
# ------------------------------
@app.post("/scan")
async def scan_project(req: Request):
    data = await req.json()
    with open(PROJECT_BACKUP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return {"message": "Projekt gescannt und gespeichert!", "files": len(data.get("files", []))}

# ------------------------------
# Chat Endpoint
# ------------------------------
@app.post("/chat")
async def chat_with_ai(req: Request):
    body = await req.json()
    user_message = body.get("message", "")

    context = ""
    if os.path.exists(PROJECT_BACKUP_FILE):
        with open(PROJECT_BACKUP_FILE, "r", encoding="utf-8") as f:
            context = f.read()

    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": HTTP_REFERER,
            "X-Title": X_TITLE
        },
        model="deepseek/deepseek-chat-v3.1:free",
        messages=[
            {"role": "system", "content": "Du bist eine Roblox-Scripting-KI, die Code sicher erstellt."},
            {"role": "user", "content": f"Projektkontext:\n{context}\n\nNutzeranfrage:\n{user_message}"}
        ]
    )

    return {"response": completion.choices[0].message.content}
